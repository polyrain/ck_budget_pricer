import requests
from html.parser import HTMLParser
import tkinter as tk
from time import sleep



class MyHTMLParser(HTMLParser):
    def __init__(self, card_name):
        super().__init__()
        self.num_valid = 0
        self.card_name = card_name
        self.total_price = 0
        self.new_item = False
        self.valid_item = False
        self.potential_price = False
        self.card_variants = [" (Promo Pack)", " (Prerelease Foil)", " (Buy-a-Box Foil)", " (Borderless)", " (Extended Art)", " (Showcase)", " (Brawl Deck Card)", " (Foil)"]
        self.valid_cards = ["catalogItem cardItem noBorder", "catalogItem cardItem black", "catalogItem cardItem white"]
        self.valid_quals = ["itemAddToCart  outOfStock  NM active", "itemAddToCart  outOfStock  NM ", "itemAddToCart  NM active"]
        self.prices = []
        self.exact_item = False

    def print_prices(self):
        print(self.prices)
    def print_valid(self):
        print(self.num_valid)

    def cheapest(self):
        if (len(self.prices) == 0):
            print("Invalid card: " + str(self.card_name))
            return -10000000 # If you had a bad card this will spit it back at you
        return min(self.prices)

    def handle_starttag(self, tag, attrs):
        if (self.new_item): # If we've seen a match
            if (attrs[0][1] in self.valid_cards):
                self.num_valid = self.num_valid + 1 # Here is where we need to do the pattern match
                self.valid_item = True # Potentially a valid item here, in terms of "legality"
            self.new_item = False
            
        if (self.exact_item): # If this is EXACTLY a card we can check
            if (tag == 'li' and len(attrs) > 0 and attrs[0][1] in self.valid_quals):
                    self.potential_price = True # Grab the NM version only
                    self.exact_item = False

        if (tag == "div" and len(attrs) > 0 and attrs[0][0] == "class" and attrs[0][1] == 'productItemWrapper productCardWrapper '):
            self.new_item = True # First flag says we found a potential match

    def handle_data(self, data):

        if (self.valid_item):
            if (data.lower() == self.card_name.lower()):
                self.valid_item = False
                self.exact_item = True
            else:
                for variant in self.card_variants:
                    var_card = str(data).replace(variant, "")
                    
                    if (self.card_name.lower() == var_card.lower()):
                        self.valid_item = False
                        self.exact_item = True
                        break
                    
        if ('$' in data and self.potential_price):
            self.potential_price = False
            processed_data = ("".join(data.split())).replace("$","")
            self.prices.append(float(processed_data))

def construct_link(card_name):
    card_words = card_name.split() # if there's only one word it will just be the original name
    final_link = "https://www.cardkingdom.com/catalog/search?filter%5Bipp%5D=60&filter%5Bsort%5D=name&filter%5Bname%5D=" 
    for word in card_words:
        final_link = final_link + word + "+"
    return final_link[:-1]
#https://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=WORD+WORD+WORD

#https://www.cardkingdom.com/catalog/search?filter%5Bipp%5D=60&filter%5Bsort%5D=name&filter%5Bname%5D=Sol+Ring


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Budget EDH Pricer")
        self.deck_data = None
        self.label = tk.Label(master, text="Enter your deck in box below.")
        self.label.pack()

        self.text_box = tk.Text(master, height=40, width=80)
        self.text_box.pack()

        self.card_label = tk.Label(master, text="Processing nothing!")
        self.card_label.pack()
        self.price_label = tk.Label(master, text="Your deck currently costs: 0.0")
        self.price_label.pack()

        self.greet_button = tk.Button(master, text="Price it up!", command=self.price, fg="black")
        self.greet_button.pack()

        self.close_button = tk.Button(master, text="Close", command=master.quit, fg="black")
        self.close_button.pack()

        self.cost = 0.0

    def price(self):
        self.cost = 0.0
        deck_data = self.text_box.get("1.0",'end-1c')
        
        # Go over every card
        for line in deck_data.splitlines():
            print("Pricing: " + line)
            if (line.strip() and line.replace(" ", "")):
                
                line = line.rstrip()
                if (line[0:4] == "1 x "):
                    line = line[4:]
                elif (line[0:4] == "1 X "):
                    line = line[4:]
                elif (line[0:2] == "1 "):
                    line = line[2:]
                
                self.card_label.config(text="Currently processing: " + str(line))
                self.card_label.pack()
                r = requests.get(construct_link(line))
                parser = MyHTMLParser(line)
                parser.feed(r.text)
                print("Price for " + line + " was: " + str(parser.cheapest()))
                self.cost = self.cost + parser.cheapest()
                if (parser.cheapest() < 0):
                    self.card_label.config(text="Not recognized: " + str(line))
                    break
            #sleep(0.05)    
        self.price_label.config(text="Your deck currently costs: " + str(self.cost))





def main():
    root= tk.Tk()
    my_gui = GUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()

#<li class="itemAddToCart  NM
#<

#<li class="itemAddToCart  OutOfStock  NM
#