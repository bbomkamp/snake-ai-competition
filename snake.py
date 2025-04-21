import pygame
import random
import sys
from collections import deque

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake AI Competition")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Font for score display
font = pygame.font.SysFont("arial", 25)


class Snake:
    def __init__(self, body, direction, color):
        self.body = body
        self.direction = direction
        self.color = color

    def move(self):
        head_x, head_y = self.body[0]
        if self.direction == "UP":
            self.body.insert(0, [head_x, head_y - BLOCK_SIZE])
        elif self.direction == "DOWN":
            self.body.insert(0, [head_x, head_y + BLOCK_SIZE])
        elif self.direction == "LEFT":
            self.body.insert(0, [head_x - BLOCK_SIZE, head_y])
        elif self.direction == "RIGHT":
            self.body.insert(0, [head_x + BLOCK_SIZE, head_y])

    def grow(self):
        # Do nothing; the tail is not removed when growing
        pass

    def shrink(self):
        self.body.pop()

    def draw(self, screen):
        for segment in self.body:
            pygame.draw.rect(screen, self.color, pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_snake(snake_body, color):
    """Draw the snake on the screen."""
    for segment in snake_body:
        pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_food(food_position):
    """Draw the food on the screen."""
    pygame.draw.rect(screen, RED, pygame.Rect(food_position[0], food_position[1], BLOCK_SIZE, BLOCK_SIZE))


def display_score(score1, score2):
    """Display the current scores on the screen."""
    score_text = font.render(f"Snake 1: {score1}  Snake 2: {score2}", True, WHITE)
    screen.blit(score_text, [10, 10])


def ai_move(snake_body, food_position, direction, other_snake_body):
    """Improved AI logic to prioritize avoiding collisions over eating food."""
    head_x, head_y = snake_body[0]
    food_x, food_y = food_position

    # Possible moves
    moves = get_possible_moves(head_x, head_y)

    # Filter valid moves
    valid_moves = get_valid_moves(moves, snake_body, other_snake_body)

    # If no valid moves, continue in the current direction
    if not valid_moves:
        return direction

    # Check if the food is contested
    contested = food_position in other_snake_body[:3]  # Check if the other snake is close to the food
    if contested:
        # Avoid moving directly toward the food if it's contested
        valid_moves = {move: pos for move, pos in valid_moves.items() if pos != food_position}

    # Prioritize food among valid moves
    best_move = prioritize_food(valid_moves, food_position)

    # If no move toward the food is safe, return any valid move
    return best_move or direction


def get_possible_moves(head_x, head_y):
    """Return all possible moves from the current position."""
    return {
        "UP": [head_x, head_y - BLOCK_SIZE],
        "DOWN": [head_x, head_y + BLOCK_SIZE],
        "LEFT": [head_x - BLOCK_SIZE, head_y],
        "RIGHT": [head_x + BLOCK_SIZE, head_y],
    }


def get_valid_moves(moves, snake_body, other_snake_body):
    """Filter out moves that would result in collisions."""
    valid_moves = {}
    for move, position in moves.items():
        if (0 <= position[0] < SCREEN_WIDTH and
                0 <= position[1] < SCREEN_HEIGHT and
                position not in snake_body and
                position not in other_snake_body):
            valid_moves[move] = position
    return valid_moves


def prioritize_food(valid_moves, food_position):
    """Choose the move that minimizes the distance to the food."""
    best_move = None
    min_distance = float("inf")
    for move, position in valid_moves.items():
        distance = abs(position[0] - food_position[0]) + abs(position[1] - food_position[1])  # Manhattan distance
        if distance < min_distance:
            min_distance = distance
            best_move = move
    return best_move


def flood_fill(snake_body, other_snake_body):
    """Calculate the available space for the snake using flood-fill."""
    visited = set()
    queue = deque([snake_body[0]])
    space = 0

    while queue:
        x, y = queue.popleft()  # Faster than pop(0)
        if (x, y) in visited or (x, y) in snake_body or (x, y) in other_snake_body:
            continue
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
            continue

        visited.add((x, y))
        space += 1

        # Add neighboring cells
        queue.append((x + BLOCK_SIZE, y))
        queue.append((x - BLOCK_SIZE, y))
        queue.append((x, y + BLOCK_SIZE))
        queue.append((x, y - BLOCK_SIZE))

    return space


def spawn_food_with_safe_zone(snake1_body, snake2_body):
    """Spawn food with a safe zone around it."""
    while True:
        food_position = [random.randrange(0, SCREEN_WIDTH // BLOCK_SIZE) * BLOCK_SIZE,
                         random.randrange(0, SCREEN_HEIGHT // BLOCK_SIZE) * BLOCK_SIZE]
        # Ensure food is not too close to either snake
        safe_zone = [
            [food_position[0] + BLOCK_SIZE, food_position[1]],
            [food_position[0] - BLOCK_SIZE, food_position[1]],
            [food_position[0], food_position[1] + BLOCK_SIZE],
            [food_position[0], food_position[1] - BLOCK_SIZE],
        ]
        if (food_position not in snake1_body and food_position not in snake2_body and
                all(zone not in snake1_body for zone in safe_zone) and
                all(zone not in snake2_body for zone in safe_zone)):
            return food_position


def menu():
    """Display the menu and handle user input."""
    while True:
        screen.fill(BLACK)
        title_text = font.render("Snake AI Competition", True, WHITE)
        one_snake_text = font.render("Press 1 for Single Snake Mode", True, GREEN)
        two_snake_text = font.render("Press 2 for Two Snakes Mode", True, BLUE)
        quit_text = font.render("Press Q to Quit", True, RED)

        # Display menu options
        screen.blit(title_text, [SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 100])
        screen.blit(one_snake_text, [SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2])
        screen.blit(two_snake_text, [SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50])
        screen.blit(quit_text, [SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100])

        pygame.display.flip()

        # Handle menu input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # Single Snake Mode
                    main(single_snake=True)
                if event.key == pygame.K_2:  # Two Snakes Mode
                    main(single_snake=False)
                if event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    sys.exit()


def main(single_snake):
    # Initial snake setups
    snake1 = Snake([[100, 100], [80, 100], [60, 100]], "RIGHT", GREEN)  # Snake 1
    snake2 = None
    if not single_snake:
        snake2 = Snake([[700, 500], [720, 500], [740, 500]], "LEFT", BLUE)  # Snake 2

    # Initial food position
    food_position = spawn_food_with_safe_zone(snake1.body, snake2.body if snake2 else [])
    food_spawn = True

    # Initial scores
    score1 = 0
    score2 = 0

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # AI logic for Snake 1
        snake1.direction = ai_move(snake1.body, food_position, snake1.direction, snake2.body if snake2 else [])

        # AI logic for Snake 2 (if it exists)
        if snake2:
            snake2.direction = ai_move(snake2.body, food_position, snake2.direction, snake1.body)

        # Move Snake 1
        snake1.move()

        # Move Snake 2 (if it exists)
        if snake2:
            snake2.move()

        # Check if Snake 1 eats the food
        if snake1.body[0][0] == food_position[0] and snake1.body[0][1] == food_position[1]:
            score1 += 1
            food_spawn = False
        else:
            snake1.shrink()

        # Check if Snake 2 eats the food (if it exists)
        if snake2 and snake2.body[0][0] == food_position[0] and snake2.body[0][1] == food_position[1]:
            score2 += 1
            food_spawn = False
        elif snake2:
            snake2.shrink()

        # Spawn new food if needed
        if not food_spawn:
            food_position = spawn_food_with_safe_zone(snake1.body, snake2.body if snake2 else [])
            food_spawn = True

        # Check for collisions
        # Wall collision for Snake 1
        if (snake1.body[0][0] < 0 or snake1.body[0][0] >= SCREEN_WIDTH or
                snake1.body[0][1] < 0 or snake1.body[0][1] >= SCREEN_HEIGHT):
            if snake2:
                print("Snake 2 Wins!")
            else:
                print("Game Over!")
            return  # Return to menu

        # Wall collision for Snake 2 (if it exists)
        if snake2 and (snake2.body[0][0] < 0 or snake2.body[0][0] >= SCREEN_WIDTH or
                       snake2.body[0][1] < 0 or snake2.body[0][1] >= SCREEN_HEIGHT):
            print("Snake 1 Wins!")
            return  # Return to menu

        # Self-collision for Snake 1
        for segment in snake1.body[1:]:
            if snake1.body[0] == segment:
                if snake2:
                    print("Snake 2 Wins!")
                else:
                    print("Game Over!")
                return  # Return to menu

        # Self-collision for Snake 2 (if it exists)
        if snake2:
            for segment in snake2.body[1:]:
                if snake2.body[0] == segment:
                    print("Snake 1 Wins!")
                    return  # Return to menu

        # Collision between Snake 1 and Snake 2 (if both exist)
        if snake2:
            for segment in snake2.body:
                if snake1.body[0] == segment:
                    print("Collision! It's a draw!")
                    return  # Return to menu

            for segment in snake1.body:
                if snake2.body[0] == segment:
                    print("Snake 1 Wins!")
                    return  # Return to menu

        # Clear the screen
        screen.fill(BLACK)

        # Draw the snakes and food
        snake1.draw(screen)
        if snake2:
            snake2.draw(screen)
        draw_food(food_position)

        # Display the scores
        if snake2:
            display_score(score1, score2)
        else:
            display_score(score1, 0)

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(36)  # Increase frame rate to 20 FPS


if __name__ == "__main__":
    menu()