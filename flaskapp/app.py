from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from deck_of_cards import deck_of_cards

app = Flask(__name__)
app.secret_key = 'supersecretkey'
deck_obj = deck_of_cards.DeckOfCards()

# Database setup
# def init_db():
#     conn = sqlite3.connect('blackjack.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             balance INTEGER DEFAULT 1000
#         )
#     ''')
#     conn.commit()
#     conn.close()


def init_db():
    conn = sqlite3.connect('blackjack.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            total_balance INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
init_db()

# Define global variables
dealer_cards = []
user_cards = []

# Function to get deck value
# def getDeckValue(deck):
#     aceFlag = False
#     deckValue = 0
#     deckValueWithAce11 = 0

#     for card in deck:
#         if card.rank == 1:
#             aceFlag = True
#             deckValue += 1
#             deckValueWithAce11 += 11
#         elif card.value > 10:
#             deckValue += 10
#             deckValueWithAce11 += 10
#         else:
#             deckValue += card.value
#             deckValueWithAce11 += card.value

#     return (deckValue, deckValueWithAce11, aceFlag)

def getDeckValue(deck):
    deck_value = 0
    ace_flag = False

    for card in deck:
        if card.rank == 1:  # Ace
            if deck_value + 11 <= 21:
                deck_value += 11
                ace_flag = True
            else:
                deck_value += 1
        elif card.value > 10:  # Face cards
            deck_value += 10
        else:  # Number cards
            deck_value += card.value

    return (deck_value, ace_flag)


# Function to deal initial cards
# def deal_initial_cards():
#     global dealer_cards, user_cards
#     dealer_cards = []
#     user_cards = []
    
#     # Dealer's cards
#     dealer_cards.append(deck_obj.give_random_card())
#     dealer_cards.append(deck_obj.give_random_card())
    
#     # User's cards
#     user_cards.append(deck_obj.give_random_card())
#     user_cards.append(deck_obj.give_random_card())

def deal_initial_cards():
    global dealer_cards, user_cards
    deck_obj.reset_deck()  # Reset the deck
    dealer_cards = []
    user_cards = []
    
    # Dealer's cards
    dealer_cards.append(deck_obj.give_random_card())
    dealer_cards.append(deck_obj.give_random_card())
    
    # User's cards
    user_cards.append(deck_obj.give_random_card())
    user_cards.append(deck_obj.give_random_card())
# Function to add a card to user's hand
# def hit():
#     global user_cards
#     user_cards.append(deck_obj.give_random_card())
#     return getDeckValue(user_cards)

def hit():
    global user_cards
    user_cards.append(deck_obj.give_random_card())
    return getDeckValue(user_cards)

# # Function to determine game result
# def determine_winner(user_value, dealer_value):
#     if user_value[0] > 21:
#         return "You busted! Dealer wins."
#     elif dealer_value[0] > 21:
#         return "Dealer busted! You win!"
#     elif user_value[1] == 21 and len(user_cards) == 2 and dealer_value[1] != 21:
#         return "Blackjack! You win!"
#     elif dealer_value[1] == 21 and len(dealer_cards) == 2 and user_value[1] != 21:
#         return "Dealer has Blackjack! Dealer wins!"
#     elif user_value[0] == 21 and len(user_cards) == 2 and dealer_value[0] == 21 and len(dealer_cards) == 2:
#         return "You both hit a blackjack! It's a tie!"
#     elif user_value[0] == dealer_value[0]:
#         return "It's a tie!"
#     elif user_value[0] > dealer_value[0]:
#         return "You win!"
#     else:
#         return "Dealer wins!"

# Function to determine game result
# def determine_winner(user_value, dealer_value):
#     if user_value[0] > 21:
#         return "You busted! Dealer wins."
#     elif dealer_value[0] > 21:
#         return "Dealer busted! You win!"
#     elif user_value[1] == 21 and len(user_cards) == 2 and dealer_value[1] != 21:
#         return "Blackjack! You win!"
#     elif dealer_value[1] == 21 and len(dealer_cards) == 2 and user_value[1] != 21:
#         return "Dealer has Blackjack! Dealer wins!"
#     elif user_value[0] == 21 and len(user_cards) == 2 and dealer_value[0] == 21 and len(dealer_cards) == 2:
#         return "You both hit a blackjack! It's a tie!"
#     elif user_value[0] == dealer_value[0]:
#         return "It's a tie!"
#     elif user_value[0] > dealer_value[0]:
#         return "You win!"
#     else:
#         return "Dealer wins."

def determine_winner(user_value, dealer_value):
    user_score, user_has_ace = user_value
    dealer_score, dealer_has_ace = dealer_value

    if user_score > 21:
        if user_has_ace:
            user_score -= 10
            user_has_ace = False
        else:
            return "You busted! Dealer wins."

    if dealer_score > 21:
        if dealer_has_ace:
            dealer_score -= 10
            dealer_has_ace = False
        else:
            return "Dealer busted! You win."

    if user_score == 21 and len(user_cards) == 2 and dealer_score != 21:
        return "Blackjack! You win!"
    elif dealer_score == 21 and len(dealer_cards) == 2 and user_score != 21:
        return "Dealer has Blackjack! Dealer wins!"
    elif user_score == 21 and len(user_cards) == 2 and dealer_score == 21 and len(dealer_cards) == 2:
        return "You both hit a blackjack! It's a tie!"
    elif user_score == dealer_score:
        return "It's a tie!"
    elif user_score > dealer_score:
        return "You win!"
    else:
        return "Dealer wins."

# Function for dealer's turn
def dealer_turn():
    global dealer_cards
    dealer_value = getDeckValue(dealer_cards)
    
    # Dealer hits until their total is 17 or higher
    while dealer_value[0] < 17:
        dealer_cards.append(deck_obj.give_random_card())
        dealer_value = getDeckValue(dealer_cards)
    
    return dealer_value

# Route to display the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route to register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        conn = sqlite3.connect('blackjack.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username) VALUES (?)', (username,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists!"
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Route to login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        conn = sqlite3.connect('blackjack.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['balance'] = user[2]  # Assuming the balance is in the third column
            return redirect(url_for('index'))
        return "Invalid username!"
    return render_template('login.html')

# Route to logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('balance', None)
    return redirect(url_for('index'))

# Route to start the game
@app.route('/start_game', methods=['POST'])
def start_game():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('bet.html', realAmount=0, total_balance=session['balance'])

# # Route to handle bet submission
# @app.route('/place_bet', methods=['POST'])
# def place_bet():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     bet_amount = int(request.form['bet_amount'])
    
#     # Check if bet amount is more than the balance
#     if bet_amount > session['balance']:
#         return "You cannot bet more than your current balance!"
    
#     session['realAmount'] = bet_amount
#     deal_initial_cards()
#     return redirect(url_for('play_game'))

@app.route('/place_bet', methods=['POST'])
def place_bet():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    bet_amount = int(request.form['bet_amount'])
    
    # Check if bet amount is more than the balance
    if bet_amount > session['balance']:
        return "You cannot bet more than your current balance!"
    
    # Update realAmount and total_balance in session
    session['realAmount'] = bet_amount
    session['total_balance'] = session['balance']
    
    deal_initial_cards()
    return redirect(url_for('play_game'))


# Route to play the game
@app.route('/play_game')
def play_game():
    if 'username' not in session:
        return redirect(url_for('login'))
    dealer_value = getDeckValue(dealer_cards)
    user_value = getDeckValue(user_cards)
    return render_template('play.html', dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# Route to handle user hitting
@app.route('/hit', methods=['POST'])
def hit_endpoint():
    if 'username' not in session:
        return redirect(url_for('login'))
    global user_cards
    user_value = hit()
    
    # Check if user busted
    if user_value[0] > 21:
        dealer_value = dealer_turn()
        result = "You busted! Dealer wins."
        update_balance(-session['realAmount'])
        return render_template('result.html', result=result, dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)
    else:
        dealer_value = getDeckValue(dealer_cards)
        return render_template('play.html', dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# Route to handle user standing
# @app.route('/stand', methods=['POST'])
# def stand():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     dealer_value = dealer_turn()
#     user_value = getDeckValue(user_cards)
    
#     result = determine_winner(user_value, dealer_value)
    
#     if "win" in result.lower():
#         update_balance(session['realAmount'])
#     else:
#         update_balance(-session['realAmount'])
        
#     return render_template('result.html', result=result, dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)


# # Route to handle user standing
# @app.route('/stand', methods=['POST'])
# def stand():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     dealer_value = dealer_turn()
#     user_value = getDeckValue(user_cards)
    
#     result = determine_winner(user_value, dealer_value)
    
#     if "you win" in result.lower():
#         update_balance(session['realAmount'])
#     elif "dealer wins" in result.lower():
#         update_balance(-session['realAmount'])
#     # No balance update on tie
    
#     return render_template('result.html', result=result, dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# Route to handle user standing
@app.route('/stand', methods=['POST'])
def stand():
    if 'username' not in session:
        return redirect(url_for('login'))
    dealer_value = dealer_turn()
    user_value = getDeckValue(user_cards)
    
    result = determine_winner(user_value, dealer_value)
    
    if "you win" in result.lower():
        update_balance(session['realAmount'])
    elif "dealer wins" in result.lower():
        update_balance(-session['realAmount'])
    # No balance update on tie or dealer bust
    
    return render_template('result.html', result=result, dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# Function to update user balance
def update_balance(amount):
    conn = sqlite3.connect('blackjack.db')
    c = conn.cursor()
    c.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, session['username']))
    conn.commit()
    session['balance'] += amount  # Update session balance
    conn.close()

# Route to play again
@app.route('/play_again', methods=['POST'])
def play_again():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('start_game'))

@app.route('/leaderboard')
def leaderboard():
    conn = sqlite3.connect('blackjack.db')
    c = conn.cursor()
    c.execute('SELECT username, total_balance FROM players ORDER BY total_balance DESC LIMIT 10')
    top_scorers = c.fetchall()
    conn.close()
    return render_template('leaderboard.html', top_scorers=top_scorers)

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, redirect, url_for, session
# from deck_of_cards import deck_of_cards

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'

# deck_obj = deck_of_cards.DeckOfCards()

# # Serialization and deserialization functions
# def card_to_dict(card):
#     return {'rank': card.rank, 'suit': card.suit}

# def dict_to_card(card_dict):
#     return deck_of_cards.Card(card_dict['rank'], card_dict['suit'])

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/start_game', methods=['POST'])
# def start_game():
#     session['dealer_cards'] = []
#     session['user_cards'] = []
#     session['player_chips'] = 1000
#     session['bet_amount'] = 0

#     dealer_cards = [deck_obj.give_random_card() for _ in range(2)]
#     user_cards = [deck_obj.give_random_card() for _ in range(2)]

#     session['dealer_cards'] = [card_to_dict(card) for card in dealer_cards]
#     session['user_cards'] = [card_to_dict(card) for card in user_cards]

#     return redirect(url_for('game'))

# @app.route('/game')
# def game():
#     dealer_cards = [dict_to_card(card_dict) for card_dict in session['dealer_cards']]
#     user_cards = [dict_to_card(card_dict) for card_dict in session['user_cards']]

#     dealer_value = getDeckValue(dealer_cards)
#     user_value = getDeckValue(user_cards)

#     return render_template('game.html', dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# @app.route('/hit')
# def hit():
#     user_cards = [dict_to_card(card_dict) for card_dict in session['user_cards']]
#     user_cards.append(deck_obj.give_random_card())
#     session['user_cards'] = [card_to_dict(card) for card in user_cards]

#     user_value = getDeckValue(user_cards)
#     if user_value[0] > 21:
#         return redirect(url_for('game_over', result='bust'))
#     return redirect(url_for('game'))

# @app.route('/stand')
# def stand():
#     dealer_cards = [dict_to_card(card_dict) for card_dict in session['dealer_cards']]
#     dealer_value = getDeckValue(dealer_cards)

#     while dealer_value[0] < 17 and dealer_value[1] < 17:
#         dealer_cards.append(deck_obj.give_random_card())
#         dealer_value = getDeckValue(dealer_cards)

#     session['dealer_cards'] = [card_to_dict(card) for card in dealer_cards]
#     return redirect(url_for('game_over', result='stand'))

# @app.route('/game_over/<result>')
# def game_over(result):
#     dealer_cards = [dict_to_card(card_dict) for card_dict in session['dealer_cards']]
#     user_cards = [dict_to_card(card_dict) for card_dict in session['user_cards']]
#     dealer_value = getDeckValue(dealer_cards)
#     user_value = getDeckValue(user_cards)

#     return render_template('game_over.html', result=result, dealer_cards=dealer_cards, user_cards=user_cards, dealer_value=dealer_value, user_value=user_value)

# def getDeckValue(deck):
#     ace_flag = False
#     deck_value = 0
#     deck_value_with_ace_11 = 0

#     for card in deck:
#         if card.rank == 1:
#             ace_flag = True
#             deck_value += 1
#             deck_value_with_ace_11 += 11
#         elif card.value > 10:
#             deck_value += 10
#             deck_value_with_ace_11 += 10
#         else:
#             deck_value += card.value
#             deck_value_with_ace_11 += card.value

#     return (deck_value, deck_value_with_ace_11, ace_flag)

# if __name__ == '__main__':
#     app.run(debug=True)


####################################
# from flask import Flask, render_template,request, redirect, url_for
# from operator import itemgetter

# app = Flask(__name__)

# from deck_of_cards import deck_of_cards

# deck_obj = deck_of_cards.DeckOfCards()



# def getBetAmount():
#     global realAmount
#     realAmount = 0
#     continueFlag = True
#     print("Would you like to place a bet?\n")
#     while continueFlag == True:
#         betAmount = str(input("Add chips? (1 = 25 chips, 2 = 50 chips, 3 = 100 chips, q = Continue)\n"))
#         if betAmount == "q" and realAmount == 0:
#             print("\nThank you for playing!\n")
#             break
#         elif betAmount == "q" and realAmount != 0:
#             print("\nYou have placed a bet of "+str(realAmount)+" tokens. Good luck!\n")
#             continueFlag = False
#         elif betAmount == "1":
#             realAmount += 25
#         elif betAmount == "2":
#             realAmount += 50
#         elif betAmount == "3":
#             realAmount += 100
#         else:
#             print("Please enter a valid bet")


# def getDeckValue(deck):
#     aceFlag = False
#     deckValue = 0
#     deckValueWithAce11= 0 

#     for card in deck:
#         if card.rank == 1:
#             aceFlag = True
#             deckValue += 1
#             deckValueWithAce11 += 11
#         elif card.value > 10:
#             deckValue += 10
#             deckValueWithAce11 += 10
#         else:
#             deckValue += card.value
#             deckValueWithAce11 += card.value

#     return (deckValue,deckValueWithAce11,aceFlag)


# def Game():
#     print("Welcome to Intern Amy's Blackjack Extravaganza!\n")
#     getBetAmount()

#     dealerCards = []
#     userCards = []
#     player_chips = 1000  # ####Starting chips

#     # ###dealer pulls first card
#     tempDealerCard = deck_obj.give_random_card()
#     dealerCards.append(tempDealerCard)
#     curDealerValue = getDeckValue(dealerCards)

#     if curDealerValue[2] == True:
#         print("The Dealer pulled a "+tempDealerCard.name+" ("+str(getDeckValue(dealerCards)[0])+"/"+str(getDeckValue(dealerCards)[1])+").\n")
#     else:
#         print("The Dealer pulled a "+tempDealerCard.name+" ("+str(getDeckValue(dealerCards)[0])+").\n")

#     ##### user pulls first card
#     tempUserCard = deck_obj.give_random_card()
#     userCards.append(tempUserCard)
#     curUserValue = getDeckValue(userCards)

#     if curUserValue[2] == True:
#         print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+"/"+str(getDeckValue(userCards)[1])+").\n")
#     else:
#         print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+").\n")

#     # ##dealer non visible card
#     dealerCards.append(deck_obj.give_random_card())
#     print("The Dealer pulled a second card.\n") # add lowest possible value later
#     ### print(str(getDeckValue(dealerCards)[0]))

#     # ##user second card
#     tempUserCard = deck_obj.give_random_card()
#     userCards.append(tempUserCard)
#     curUserValue = getDeckValue(userCards)

#     if curUserValue[2] == True:
#         print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+"/"+str(getDeckValue(userCards)[1])+").\n")
#     else:
#         print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+").\n")

#     print("Your turn.\n")
#     while True: 
#         userChoice = input("Would you like to hit? Enter 'y' for yes and 'n' for no\n")
#         if userChoice == 'y':
#             new_card = deck_obj.give_random_card()
#             userCards.append(new_card)
#             curUserValue = getDeckValue(userCards)
#             if curUserValue[2] == True:
#                 print("\nYou pulled a "+new_card.name+" ("+str(curUserValue[0])+"/"+str(curUserValue[1])+").\n")
#             else:
#                 print("\nYou pulled a "+new_card.name+" ("+str(curUserValue[0])+").\n")
#             if curUserValue[0] > 21:
#                 print("You busted!\n")
#                 break
#         elif userChoice == 'n':
#             print("\nYou chose to stand.\n")
#             break
#         else:
#             print("Please enter a valid choice.\n")

#     if curUserValue[0] <= 21:
#         print("Dealer's turn.\n")
#         #### Reveal second card
#         if curDealerValue[2] == True:
#             print("The Dealer flips their second card, revealing a "+dealerCards[1].name+" ("+str(getDeckValue(dealerCards)[0])+"/"+str(getDeckValue(dealerCards)[1])+").\n")
#         else:
#             print("The Dealer flips their second card, revealing a "+dealerCards[1].name+" ("+str(getDeckValue(dealerCards)[0])+").\n")

#         if curDealerValue[0] >= 17 or curDealerValue[1] >= 17:
#             print("The dealer stood.\n")
#         while curDealerValue[0] < 17 and curDealerValue[1] < 17:
#             new_card = deck_obj.give_random_card()
#             dealerCards.append(new_card)
#             curDealerValue = getDeckValue(dealerCards)
#             if curDealerValue[0] > 21 and curDealerValue[1] > 21:
#                 if curDealerValue[2] == True:
#                     print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+"/"+str(curDealerValue[1])+").\n")
#                 elif curDealerValue[2] == False:
#                     print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+").\n")
#                 print("The Dealer busted!\n")
#                 break
#             elif curDealerValue[2] == True:
#                 print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+"/"+str(curDealerValue[1])+").\n")
#             elif curDealerValue[2] == False:
#                 print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+").\n")

#     # ###Check for Blackjack tie
#     if (curUserValue[0] == 21 or curUserValue[1] == 21) and (curDealerValue[0] == 21 or curDealerValue[1] == 21):
#         print("You both hit a blackjack! It's a tie!")

#     ### Check for individual Blackjacks
#     elif curUserValue[0] == 21 or curUserValue[1] == 21:
#         print("Blackjack! You win!")
#     elif curDealerValue[0] == 21 or curDealerValue[1] == 21:
#         print("Dealer has Blackjack! Dealer wins!")

#     # ##Compare hand values
#     if curUserValue[0] > 21 and curUserValue[1] > 21:
#         print("You busted! Dealer wins.")
#     elif curDealerValue[0] > 21:
#         print("Dealer busted! You win!")
#     elif curUserValue[0] > curDealerValue[0]:
#         print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. You win!")
#     elif curUserValue[0] < curDealerValue[0]:
#         print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. Dealer wins!")
#     else:
#         print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. It's a tie!")


# Game()
