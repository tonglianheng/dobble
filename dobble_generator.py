#!/usr/bin/env python
import sys
import random

class Helper:
    "helper class"
    def Print(self):
        sys.stderr.write("""
usage:

  %s [options] <num_symbols> <num_symbols_per_card>

Generates the dobble game card combinations for a given number of
symbols available and the number of symbols on each card.

<num_symbols>            total number of symbols available
<num_symbols_per_card>   number of symbols per card

options:
  --help                print help message

  -r <num_reserve>      sets the number of symbols at the end of the symbol list
                        to be used as reserve symbols, which will only be used
                        to fill in the cards when the cards cannot be completed
                        when constructed using non-reserve symbols.

  -g <num_in_group>     restricts the maximum number of cards starting with the
                        same symbol to <num_in_group>

  -gl <num_in_group>    Same as -g option, but with the last group unrestricted.

  -rs                   Enable random sampling on the list of available symbols
                        during generation of the card set. This can often
                        increase the size of the card set generated.

  --shuffle             Shuffle the symbols on each card when they are printed
                        out. This only affects output.

(c) Lianheng Tong, tonglianheng@gmail.com,  Monday, 2014/04/21

""" \
                         % (sys.argv[0]))

class Symbol:
    "Dobble card symbol class"
    mUniqueID = 0
    def __init__(self, value):
        self.mID = self.__class__.mUniqueID
        self.mValue = value
        self.__class__.mUniqueID += 1
    def ID(self):
        "Returns symbol ID"
        return self.mID
    def Value(self):
        "Returns symbol value"
        return self.mValue
    def SetValue(self, value):
        "Changes symbol value to value"
        self.mValue = value
    def Print(self):
        "Print symbol value"
        if type(self.mValue) == type(str()):
            print "%s" % (self.mValue),
        elif type(self.mValue) == type(int()):
            print "% 4d" % (self.mValue),
        elif type(self.mValue) == type(float()):
            print "% 10.7f" % (self.mValue),

class Card:
    "Dobble card class"
    mUniqueID = 0
    def __init__(self, symbols=[]):
        # default gives empty card
        assert type(symbols) == type(list())
        self.mID = self.__class__.mUniqueID
        self.mNSymbols = len(symbols)
        self.mSymbols = symbols
        self.__class__.mUniqueID += 1
    def ID(self):
        "Returns card ID"
        return self.mID
    def Symbols(self):
        "Returns the card symbols in a list"
        return self.mSymbols
    def NSymbols(self):
        "Returns the total number of symbols in the card"
        return self.mNSymbols
    def SetSymbol(self, n, symbol):
        "Changes the n-th symbol in the card to symbol. The card must have more than n symbols."
        assert n < self.mNSymbols
        self.mSymbols[n] = symbol
    def AddSymbol(self, symbol):
        "Addes symbol to card"
        self.mSymbols.append(symbol)
        self.mNSymbols += 1
    def RemoveSymbol(self, symbol):
        "Remove symbol if it is present in the card, otherwise do nothing"
        tmp_list = []
        for symb in self.mSymbols:
            if symb.ID() != symbol.ID():
                tmp_list.append(symb)
        self.mNSymbols = len(tmp_list)
        self.mSymbols = tmp_list
    def Print(self, shuffleSymbols):
        "Print card"
        if shuffleSymbols:
            shuffled_list = random.sample(self.mSymbols, self.mNSymbols)
        else:
            shuffled_list = self.mSymbols
        for symb in shuffled_list:
            symb.Print()
        print ""

class CardSet:
    "Dobble game card set"
    def __init__(self, symbols, nSymbolsPerCard, nReserve=0, \
                 maxGroupSize=None, restrictLastGroup=True, \
                 shuffleSymbolsSample=False):
        self.mTotalNSymbols = len(symbols)
        self.mNSymbolsPerCard = nSymbolsPerCard
        self.mMaxGroupSize = maxGroupSize
        self.mRestrictLastGroup = restrictLastGroup
        self.mShuffleSymbolsSample = shuffleSymbolsSample
        self.mNReserve = nReserve
        self.mSymbols = symbols
        self.mCards = []
        self.mNCards = len(self.mCards)
        self.mAlreadyHas = {}
        self.mCandidate = {}
        self.mReserve = []
        for symb in self.mSymbols:
            self.mCandidate[symb.ID()] = True
        # set the reseve symbols
        start = self.mTotalNSymbols - self.mNReserve
        end = self.mTotalNSymbols
        for ii in range(start, end):
            self.mReserve.append(self.mSymbols[ii])
    def AddCardToAlreadyHasList(self, symbol, card):
        "(For internal use only) Adds card to the already_has table corresponding to the symbol."
        if self.mAlreadyHas.has_key(symbol.ID()):
            self.mAlreadyHas[symbol.ID()].append(card)
        else:
            self.mAlreadyHas[symbol.ID()] = [card]
    def SetInitCard(self, card):
        "Sets the initial card, must be called when there are no cards in the card set"
        # must be called when there are no cards
        assert len(self.mCards) == 0
        self.mCards.append(card)
        for symb in card.Symbols():
            self.AddCardToAlreadyHasList(symb, card)
    def AddSymbolToProspectiveCard(self, symbol, card):
        "(For internal use only) Add symbol to the prospective card, and update candidate table. Return True if the card is compele, otherwise return False."
        card.AddSymbol(symbol)
        if card.NSymbols() == self.mNSymbolsPerCard:
            card_complete = True
        else:
            card_complete = False
        self.mCandidate[symbol.ID()] = False
        # check if symb already exists in other cards, if so, then
        # all symbols contained in those cards cannot be
        # candidates
        if symbol.ID() in self.mAlreadyHas:
            for cc in self.mAlreadyHas[symbol.ID()]:
                for ss in cc.Symbols():
                    self.mCandidate[ss.ID()] = False
        return card_complete
    def Generate(self):
        "Generates the card set, must be called after the SetInitCard() function is called."
        # must be called after SetInitCard
        assert len(self.mCards) > 0
        # every non-init card should have one symbol same as one in
        # the init card
        for ind in range(self.mNSymbolsPerCard):
            symb_i = self.mCards[0].Symbols()[ind]
            still_cards_left = True
            n_cards_in_group = 0
            while (still_cards_left):
                # reset the candidate table
                for key in self.mCandidate.keys():
                    self.mCandidate[key] = True
                # create a new blank card
                card = Card([])
                # add first symbol
                card_complete = self.AddSymbolToProspectiveCard(symb_i, card)
                # add additional symbols
                if not card_complete:
                    if self.mShuffleSymbolsSample:
                        shuffled_list = random.sample(self.mSymbols, len(self.mSymbols))
                    else:
                        shuffled_list = self.mSymbols
                    for symb in shuffled_list:
                        if ((self.mCandidate[symb.ID()]) and \
                            (not symb in self.mReserve)):
                            card_complete = self.AddSymbolToProspectiveCard(symb, card)
                            if card_complete: break
                # check if need to use the reserve symbols
                if not card_complete:
                    if self.mShuffleSymbolsSample:
                        shuffled_list = random.sample(self.mReserve, len(self.mReserve))
                    else:
                        shuffled_list = self.mReserve
                    for symb in shuffled_list:
                        if (self.mCandidate[symb.ID()]):
                            card_complete = self.AddSymbolToProspectiveCard(symb, card)
                            if card_complete: break
                # add the card to the card set if the card is compele,
                # and update the already_has table
                if card_complete:
                    self.mCards.append(card)
                    for symb in card.Symbols():
                        self.AddCardToAlreadyHasList(symb, card)
                    n_cards_in_group += 1
                else:
                    still_cards_left = False
                # restrict the number of cards starting with the same
                # initial symbol. Since the first card starts with the
                # same symbol as the case ind = 0, we need to make
                # correction in the case of ind = 0 here.
                restrict_group = (ind < self.mNSymbolsPerCard - 1) or \
                                 self.mRestrictLastGroup
                if (self.mMaxGroupSize != None) and restrict_group:
                    if ind == 0:
                        if n_cards_in_group >= self.mMaxGroupSize - 1:
                            still_cards_left = False
                    else:
                        if n_cards_in_group >= self.mMaxGroupSize:
                            still_cards_left = False
        self.mNCards = len(self.mCards)
    def Card(self, n):
        "Returns the n-th card"
        return self.mCards[n]
    def NCards(self):
        "Returns the total number of cards"
        return self.mNCards
    def Print(self, shuffle_symbols):
        "Print card set"
        for card in self.mCards:
            card.Print(shuffle_symbols)


######################################################################
# MAIN PROGRAM                                                       #
######################################################################

hp = Helper()

if (len(sys.argv) < 3) or ("--help" in sys.argv):
    hp.Print()
    sys.exit()

arg_start = 1

if "-r" in sys.argv:
    ind = sys.argv.index("-r")
    n_reserve = int(sys.argv[ind+1])
    arg_start += 2
else:
    n_reserve = 0

if "-g"  in sys.argv:
    ind = sys.argv.index("-g")
    max_group_size = int(sys.argv[ind+1])
    restrict_last_group = True
    arg_start += 2
else:
    max_group_size = None
    restrict_last_group = False

if "-gl" in sys.argv:
    ind = sys.argv.index("-gl")
    max_group_size = int(sys.argv[ind+1])
    restrict_last_group = False
    arg_start += 2
else:
    max_group_size = None
    restrict_last_group = False

if "-rs" in sys.argv:
    random_sampling = True
    arg_start += 1
else:
    random_sampling = False

if "--shuffle" in sys.argv:
    shuffle_symbols = True
    arg_start += 1
else:
    shuffle_symbols = False

total_n_symbols = int(sys.argv[arg_start])
n_symbols_per_card = int(sys.argv[arg_start+1])

# setup symbols
symbols = []
for ii in range(total_n_symbols):
    value = ii + 1
    symbols.append(Symbol(value))

# setup Dobble game card set
card_set = CardSet(symbols, n_symbols_per_card, n_reserve, \
                   max_group_size, restrict_last_group, \
                   random_sampling)
init_card = Card([])
for ii in range(n_symbols_per_card):
    init_card.AddSymbol(symbols[ii])
card_set.SetInitCard(init_card)
card_set.Generate()
print "# Number of Symbols: %d" % total_n_symbols
print "# Number of Symbols per card: %d" % n_symbols_per_card
print "# Total number of cards: %d" % card_set.NCards()
card_set.Print(shuffle_symbols)
