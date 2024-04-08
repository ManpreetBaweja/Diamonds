
import pygame
import random

class Card:
  def __init__(self, suit, value):
    self.suit = suit
    self.value = value

  def __str__(self):
    face_cards = {11: "jack", 12: "queen", 13: "king", 14: "ace"}
    return f"{face_cards.get(self.value, self.value)} of {self.suit}"
  
  def copy(self):
    return Card(self.suit, self.value)  # Create a new Card object with the same suit and value




class Deck:
  def __init__(self):
    suits = ["spades", "hearts", "clubs", "diamonds"]
    values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    self.cards = [Card(suit, value) for suit in suits for value in values if suit != "diamonds"]
    self.diamonds = [Card(suit, value) for suit in suits for value in values if suit == "diamonds"]
    random.shuffle(self.cards)
    random.shuffle(self.diamonds)

  def draw(self):
    if len(self.cards) > 0:
      return self.cards.pop()
    else:
      return None
  
  def draw_diamond(self):
    if len(self.diamonds) > 0:
      return self.diamonds.pop()
    else:
      return None
     

class Player:
  def __init__(self, name, x, y):
    self.name = name
    self.hand = []
    self.score = 0
    self.count = 0  # Initialize card count
    self.x = x  # Position for card display
    self.y = y

  def draw_cards(self, deck, num_cards):
    for _ in range(num_cards):
      card = deck.draw()
      if card is not None and card not in self.hand:
        self.hand.append(card)
        self.update_count(card)  # Update count only if card drawn

  def update_count(self, card):
    if card is None:
      return
    # Simple card counting strategy:
    # +1 for high cards (10, Jack, Queen, King)
    # -1 for low cards (2, 3, 4, 5, 6)
    if card.value in [10, 11, 12, 13]:
      self.count += 1
    elif card.value in [2, 3, 4, 5, 6]:
      self.count -= 1

  def choose_bid(self, revealed_diamond):
    # Basic Bidding Strategy with Card Counting:
    # 1. If you have a high diamond (King, Queen, Jack or 10), bid it regardless of count.
    # 2. If count is positive (more high cards seen), be more aggressive with bidding (including higher low diamonds).
    # 3. If count is negative (more low cards seen), be more conservative with bidding (only bid high diamonds).
    high_diamonds = [10, 11, 12, 13]
    low_diamonds = [2, 3, 4, 5, 6, 7, 8, 9]

    for card in self.hand:
      if card.value in high_diamonds:
        return card

    # No high diamonds, choose a bid based on count
    high_diamonds_in_hand = [card for card in self.hand if card.value in high_diamonds]
    if self.count > 0 :
      # More high cards seen, be more aggressive (use max if high diamonds exist)
      best_bid = max(high_diamonds_in_hand, key=lambda x: x.value) if high_diamonds_in_hand else min(self.hand, key=lambda x: x.value)
    else:
      # More low cards seen, be conservative (use max if high diamonds exist)
      best_bid = max(high_diamonds_in_hand, key=lambda x: x.value) if high_diamonds_in_hand else None
    return best_bid or min(self.hand, key=lambda x: x.value) # Ensure a bid is chosen even if no high diamonds

  def play_round(self, deck, revealed_diamond):
    bid = self.choose_bid(revealed_diamond)
    self.hand.remove(bid)
    return bid

  def draw(self, screen, card_image):
    for i, card in enumerate(self.hand):
      screen.blit(card_image, (self.x + i * 70, self.y))  # Adjust spacing between cards

card_width = 5  # Adjust desired card width
card_height = 7  # Adjust desired card height

# Function to load a card image based on suit and value, with optional scaling
def load_card_image(suit, value, scale=0.3):
    # Adjust file paths and image names based on your resources
    image_name = f"{value}"+"_of_"+f"{suit}.png"
    image = pygame.image.load('/home/mana/Desktop/PNG-cards-1.3/' + image_name)
    if scale:
        image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
    
    return image

pygame.init() 
class Diamonds:
  def __init__(self, width, height):
    self.deck = Deck()
    self.player1 = Player("You", 50, height - 100)
    self.player2 = Player("AI", width - 200, height - 100)
    self.width = width
    self.height = height
    self.revealed_diamond = None
    self.font = pygame.font.Font(None, 32)  # Font for text display

  def determine_winner(self, bid1, bid2):
    if bid1.value > bid2.value:
        return self.player1
    elif bid1.value < bid2.value:
        return self.player2
    else:
        return self.player2  # In case of a tie, the dealer (player2) wins

  def play_game(self):
    self.player1.draw_cards(self.deck, 3)
    self.player2.draw_cards(self.deck, 3)

    pygame.init()
    screen = pygame.display.set_mode((self.width, self.height))
    pygame.display.set_caption("Diamonds")
    clock = pygame.time.Clock()
    fps = 0.09  # Adjust FPS value to slow down the simulation (lower value = slower)

    running = True
    while running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          running = False

      screen.fill((0, 128, 0))  # Green background

      # Draw revealed diamond (if any)
      if self.revealed_diamond:
        screen.blit(load_card_image(self.revealed_diamond.suit, self.revealed_diamond.value), (self.width // 2 - 35, 50))

      # Draw player names and scores
      text_surface = self.font.render(f"{self.player1.name}: {self.player1.score}", True, (255, 255, 255))
      screen.blit(text_surface, (10, 10))
      text_surface = self.font.render(f"{self.player2.name}: {self.player2.score}", True, (255, 255, 255))
      screen.blit(text_surface, (self.width - text_surface.get_width() - 10, 10))

      card_back_image = pygame.image.load('/home/mana/Desktop/PNG-cards-1.3/card_back.jpeg')


      # Draw player hands
      for card in self.player1.hand:
        self.player1.draw(screen, load_card_image(card.suit, card.value))
      self.player2.draw(screen, card_back_image)  # AI hand remains hidden

      if len(self.deck.cards) > 0:
        self.revealed_diamond = self.deck.draw_diamond()
        print(f"Revealed Diamond: {self.revealed_diamond}")

        player1_bid = self.player1.choose_bid(self.player1.hand)
        player2_bid = random.choice(self.player2.hand)  # Choose randomly from AI's hand

        # Create copies of chosen bids for temporary display
        player1_bid_to_display = player1_bid.copy()
        player2_bid_to_display = player2_bid.copy()

        # Display chosen bids before removing from hands
        screen.blit(load_card_image(player1_bid_to_display.suit, player1_bid_to_display.value), (self.width // 4 - 35, self.height // 2))
        screen.blit(load_card_image(player2_bid_to_display.suit, player2_bid_to_display.value), (self.width * 3 // 4 - 35, self.height // 2))

        # Remove bids from hands after displaying
        self.player1.hand.remove(player1_bid)
        self.player2.hand.remove(player2_bid)

        winner = self.determine_winner(player1_bid, player2_bid)

        winner.score += self.revealed_diamond.value if self.revealed_diamond is not None else 0

      else:
        running = False
      print(f"{self.player1.name} bid: {player1_bid}, {self.player2.name} bid: {player2_bid}")
      print(f"Winner: {winner.name}\n")

      # Limit frame rate to set FPS for slowing down
      dt = clock.tick(fps) / 1000  # Get delta time in seconds

      pygame.display.flip()  # Update the display after drawing


pygame.init() 

game = Diamonds(1100, 680)
game.play_game()