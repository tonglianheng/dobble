import sys

class Helper:
    "helper class"
    def Print(self):
        sys.stderr.write("usage: %s <num_symbols> <num_symbols_per_card> [variety]" \
                         % (sys.argv[0]))
        sys.stderr.write("""
Generates the dobble game card combinations for a given number of
symbols available and the number of symbols on each card.

<num_symbols>            total number of symbols available
<num_symbols_per_card>   number of symbols per card

options:
  --help                 print help message
  [variety]              integer, for generating a different card set
""")

class Symbol:
    "Dobble card symbol class"
    mUniqueID = 0
    def __init__(self, value):
        self.mID = self.__class__.mUniqueID
        self.mValue = value
        self.__class__.mUniqueID += 1
    def ID(self):
        return self.mID
    def Value(self):
        return self.mValue
    def SetValue(self, value):
        self.mValue = value
    def Print(self):
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
        return self.mID
    def Symbols(self):
        return self.mSymbols
    def NSymbols(self):
        return self.mNSymbols
    def SetSymbol(self, n, symbol):
        self.mSymbols[n] = symbol
    def AddSymbol(self, symbol):
        self.mSymbols.append(symbol)
        self.mNSymbols += 1
    def RemoveSymbol(self, symbol):
        "remove symbol if it is present in the card, otherwise do nothing"
        tmp_list = []
        for symb in self.mSymbols:
            if symb.ID() != symbol.ID():
                tmp_list.append(symb)
        self.mNSymbols = len(tmp_list)
        self.mSymbols = tmp_list

class CardSet:
    "Dobble game card set"
    def __init__(self, symbols, nSymbolsPerCard, maxGroupSize=None):
        self.mTotalNSymbols = len(symbols)
        self.mNSymbolsPerCard = nSymbolsPerCard
        self.mMaxGroupSize = maxGroupSize
        self.mSymbols = symbols
        self.mCards = []
        self.mNCards = len(self.mCards)
        self.mAlreadyHas = {}
        self.mCandidate = {}
        for symb in self.mSymbols:
            self.mCandidate[symb.ID()] = True
    def AddCardToAlreadyHasList(self, symbol, card):
        if self.mAlreadyHas.has_key(symbol.ID()):
            self.mAlreadyHas[symbol.ID()].append(card)
        else:
            self.mAlreadyHas[symbol.ID()] = [card]
    def SetInitCard(self, card):
        # must be called when there are no cards
        assert len(self.mCards) == 0
        self.mCards.append(card)
        for symb in card.Symbols():
            self.AddCardToAlreadyHasList(symb, card)
    def Generate(self):
        # must be called after SetInitCard
        assert len(self.mCards) > 0
        # every non-init card should have one symbol same as one in
        # the init card
        for symb_i in self.mCards[0].Symbols():
            still_cards_left = True
            counter = 0
            while (still_cards_left):
                for key in self.mCandidate.keys():
                    self.mCandidate[key] = True
                card = Card([symb_i])
                card_complete = False
                self.mCandidate[symb_i.ID()] = False
                last_symbol = symb_i
                if last_symbol.ID() in self.mAlreadyHas:
                    for cc in self.mAlreadyHas[last_symbol.ID()]:
                        for ss in cc.Symbols():
                            self.mCandidate[ss.ID()] = False
                for symb in self.mSymbols:
                    # search the AlreadyHasList for last_symbol, and
                    # see if symb is found in them, if so, it cannot
                    # be a candidate
                    if self.mCandidate[symb.ID()]:
                        card.AddSymbol(symb)
                        if card.NSymbols() == self.mNSymbolsPerCard:
                            card_complete = True
                            break
                        self.mCandidate[symb.ID()] = False
                        last_symbol = symb
                        if last_symbol.ID() in self.mAlreadyHas:
                            for cc in self.mAlreadyHas[last_symbol.ID()]:
                                for ss in cc.Symbols():
                                    self.mCandidate[ss.ID()] = False
                if card_complete:
                    self.mCards.append(card)
                    for symb in card.Symbols():
                        self.AddCardToAlreadyHasList(symb, card)
                    counter += 1
                else:
                    still_cards_left = False
                if self.mMaxGroupSize != None:
                    if counter >= self.mMaxGroupSize:
                        still_cards_left = False
        self.mNCards = len(self.mCards)
    def Card(self, n):
        return self.mCards[n]
    def NCards(self):
        return self.mNCards
    def Print(self):
        for card in self.mCards:
            for symb in card.Symbols():
                symb.Print()
            print ""

# main program
hp = Helper()

if (len(sys.argv) < 3) or ("--help" in sys.argv):
    hp.Print()
    sys.exit()

total_n_symbols = int(sys.argv[1])
n_symbols_per_card = int(sys.argv[2])
if len(sys.argv) == 4:
    max_group_size = int(sys.argv[3])
else:
    max_group_size = None

# setup symbols
symbols = []
for ii in range(total_n_symbols):
    value = ii + 1
    symbols.append(Symbol(value))

# setup Dobble game card set
card_set = CardSet(symbols, n_symbols_per_card, max_group_size)
init_card = Card()
for ii in range(n_symbols_per_card):
    init_card.AddSymbol(symbols[ii])
card_set.SetInitCard(init_card)
card_set.Generate()
print "# total number of cards: %d" % card_set.NCards()
card_set.Print()
