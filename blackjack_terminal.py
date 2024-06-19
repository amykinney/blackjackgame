from flask import Flask, render_template,request, redirect, url_for
from operator import itemgetter

app = Flask(__name__)

from deck_of_cards import deck_of_cards

deck_obj = deck_of_cards.DeckOfCards()



def getBetAmount():
    global realAmount
    realAmount = 0
    continueFlag = True
    print("Would you like to place a bet?\n")
    while continueFlag == True:
        betAmount = str(input("Add chips? (1 = 25 chips, 2 = 50 chips, 3 = 100 chips, q = Continue)\n"))
        if betAmount == "q" and realAmount == 0:
            print("\nThank you for playing!\n")
            break
        elif betAmount == "q" and realAmount != 0:
            print("\nYou have placed a bet of "+str(realAmount)+" tokens. Good luck!\n")
            continueFlag = False
        elif betAmount == "1":
            realAmount += 25
        elif betAmount == "2":
            realAmount += 50
        elif betAmount == "3":
            realAmount += 100
        else:
            print("Please enter a valid bet")


def getDeckValue(deck):
    aceFlag = False
    deckValue = 0
    deckValueWithAce11= 0 

    for card in deck:
        if card.rank == 1:
            aceFlag = True
            deckValue += 1
            deckValueWithAce11 += 11
        elif card.value > 10:
            deckValue += 10
            deckValueWithAce11 += 10
        else:
            deckValue += card.value
            deckValueWithAce11 += card.value

    return (deckValue,deckValueWithAce11,aceFlag)


def Game():
    print("Welcome to Intern Amy's Blackjack Extravaganza!\n")
    getBetAmount()

    dealerCards = []
    userCards = []
    player_chips = 1000  # ####Starting chips

    # ###dealer pulls first card
    tempDealerCard = deck_obj.give_random_card()
    dealerCards.append(tempDealerCard)
    curDealerValue = getDeckValue(dealerCards)

    if curDealerValue[2] == True:
        print("The Dealer pulled a "+tempDealerCard.name+" ("+str(getDeckValue(dealerCards)[0])+"/"+str(getDeckValue(dealerCards)[1])+").\n")
    else:
        print("The Dealer pulled a "+tempDealerCard.name+" ("+str(getDeckValue(dealerCards)[0])+").\n")

    ##### user pulls first card
    tempUserCard = deck_obj.give_random_card()
    userCards.append(tempUserCard)
    curUserValue = getDeckValue(userCards)

    if curUserValue[2] == True:
        print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+"/"+str(getDeckValue(userCards)[1])+").\n")
    else:
        print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+").\n")

    # ##dealer non visible card
    dealerCards.append(deck_obj.give_random_card())
    print("The Dealer pulled a second card.\n") # add lowest possible value later
    ### print(str(getDeckValue(dealerCards)[0]))

    # ##user second card
    tempUserCard = deck_obj.give_random_card()
    userCards.append(tempUserCard)
    curUserValue = getDeckValue(userCards)

    if curUserValue[2] == True:
        print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+"/"+str(getDeckValue(userCards)[1])+").\n")
    else:
        print("You pulled a "+tempUserCard.name+" ("+str(getDeckValue(userCards)[0])+").\n")

    print("Your turn.\n")
    while True: 
        userChoice = input("Would you like to hit? Enter 'y' for yes and 'n' for no\n")
        if userChoice == 'y':
            new_card = deck_obj.give_random_card()
            userCards.append(new_card)
            curUserValue = getDeckValue(userCards)
            if curUserValue[2] == True:
                print("\nYou pulled a "+new_card.name+" ("+str(curUserValue[0])+"/"+str(curUserValue[1])+").\n")
            else:
                print("\nYou pulled a "+new_card.name+" ("+str(curUserValue[0])+").\n")
            if curUserValue[0] > 21:
                print("You busted!\n")
                break
        elif userChoice == 'n':
            print("\nYou chose to stand.\n")
            break
        else:
            print("Please enter a valid choice.\n")

    if curUserValue[0] <= 21:
        print("Dealer's turn.\n")
        #### Reveal second card
        if curDealerValue[2] == True:
            print("The Dealer flips their second card, revealing a "+dealerCards[1].name+" ("+str(getDeckValue(dealerCards)[0])+"/"+str(getDeckValue(dealerCards)[1])+").\n")
        else:
            print("The Dealer flips their second card, revealing a "+dealerCards[1].name+" ("+str(getDeckValue(dealerCards)[0])+").\n")

        if curDealerValue[0] >= 17 or curDealerValue[1] >= 17:
            print("The dealer stood.\n")
        while curDealerValue[0] < 17 and curDealerValue[1] < 17:
            new_card = deck_obj.give_random_card()
            dealerCards.append(new_card)
            curDealerValue = getDeckValue(dealerCards)
            if curDealerValue[0] > 21 and curDealerValue[1] > 21:
                if curDealerValue[2] == True:
                    print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+"/"+str(curDealerValue[1])+").\n")
                elif curDealerValue[2] == False:
                    print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+").\n")
                print("The Dealer busted!\n")
                break
            elif curDealerValue[2] == True:
                print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+"/"+str(curDealerValue[1])+").\n")
            elif curDealerValue[2] == False:
                print("The Dealer pulled a "+new_card.name+" ("+str(curDealerValue[0])+").\n")

    # ###Check for Blackjack tie
    if (curUserValue[0] == 21 or curUserValue[1] == 21) and (curDealerValue[0] == 21 or curDealerValue[1] == 21):
        print("You both hit a blackjack! It's a tie!")

    ### Check for individual Blackjacks
    elif curUserValue[0] == 21 or curUserValue[1] == 21:
        print("Blackjack! You win!")
    elif curDealerValue[0] == 21 or curDealerValue[1] == 21:
        print("Dealer has Blackjack! Dealer wins!")

    # ##Compare hand values
    if curUserValue[0] > 21 and curUserValue[1] > 21:
        print("You busted! Dealer wins.")
    elif curDealerValue[0] > 21:
        print("Dealer busted! You win!")
    elif curUserValue[0] > curDealerValue[0]:
        print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. You win!")
    elif curUserValue[0] < curDealerValue[0]:
        print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. Dealer wins!")
    else:
        print(f"Your final hand value is {curUserValue[0]}. Dealer's final hand value is {curDealerValue[0]}. It's a tie!")


Game()
