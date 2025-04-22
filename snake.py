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

    def collides_with_self(self):
        """Check if the snake collides with itself."""
        return self.body[0] in self.body[1:]

    def collides_with(self, other_snake):
        """Check if the snake collides with another snake."""
        return self.body[0] in other_snake.body


def draw_snake(snake_body, color):
    """Draw the snake on the screen."""
    for segment in snake_body:
        pygame.draw.rect(screen, color, pygame.Rect(segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))


def draw_food(food_position):
    """Draw the food on the screen."""
    pygame.draw.rect(screen, RED, pygame.Rect(food_position[0], food_position[1], BLOCK_SIZE, BLOCK_SIZE))


def display_score(green_score, blue_score):
    """Display the current scores on the screen."""
    score_text = font.render(f"Green: {green_score}  Blue: {blue_score}", True, WHITE)
    screen.blit(score_text, [10, 10])


def ai_move(snake_body, food_position, direction, other_snake_body):
    """Calculate the next move for the snake."""
    valid_moves = get_valid_moves(get_possible_moves(*snake_body[0]), snake_body, other_snake_body)

    # If no valid moves, continue in the current direction
    if not valid_moves:
        return direction

    # Prioritize food among valid moves
    return prioritize_food(valid_moves, food_position) or direction


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
    return {
        move: pos
        for move, pos in moves.items()
        if (0 <= pos[0] < SCREEN_WIDTH and
            0 <= pos[1] < SCREEN_HEIGHT and
            pos not in snake_body and
            pos not in other_snake_body)
    }


def prioritize_food(valid_moves, food_position):
    """Choose the move that minimizes the distance to the food."""
    return min(
        valid_moves,
        key=lambda move: abs(valid_moves[move][0] - food_position[0]) + abs(valid_moves[move][1] - food_position[1]),
        default=None,
    )


def flood_fill(snake_body, other_snake_body):
    """Calculate the available space for the snake using flood-fill."""
    visited = set()
    queue = deque([tuple(snake_body[0])])
    space = 0

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or (x, y) in map(tuple, snake_body) or (x, y) in map(tuple, other_snake_body):
            continue
        if x < 0 or x >= SCREEN_WIDTH or y < 0 or y >= SCREEN_HEIGHT:
            continue

        visited.add((x, y))
        space += 1

        # Add neighboring cells
        queue.extend([(x + BLOCK_SIZE, y), (x - BLOCK_SIZE, y), (x, y + BLOCK_SIZE), (x, y - BLOCK_SIZE)])

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
    snake1 = Snake([[100, 100], [80, 100], [60, 100]], "RIGHT", GREEN)  # Green Snake
    snake2 = None
    if not single_snake:
        snake2 = Snake([[700, 500], [720, 500], [740, 500]], "LEFT", BLUE)  # Blue Snake

    # Initial food position
    food_position = spawn_food_with_safe_zone(snake1.body, snake2.body if snake2 else [])
    food_spawn = True

    # Initial scores
    green_score = 0  # Green Snake's score
    blue_score = 0  # Blue Snake's score

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # AI logic for Green Snake
        snake1.direction = ai_move(snake1.body, food_position, snake1.direction, snake2.body if snake2 else [])

        # AI logic for Blue Snake (if it exists)
        if snake2:
            snake2.direction = ai_move(snake2.body, food_position, snake2.direction, snake1.body)

        # Move Green Snake
        snake1.move()

        # Move Blue Snake (if it exists)
        if snake2:
            snake2.move()

        # Check if Green Snake eats the food
        if snake1.body[0][0] == food_position[0] and snake1.body[0][1] == food_position[1]:
            green_score += 1
            food_spawn = False
        else:
            snake1.shrink()

        # Check if Blue Snake eats the food (if it exists)
        if snake2 and snake2.body[0][0] == food_position[0] and snake2.body[0][1] == food_position[1]:
            blue_score += 1
            food_spawn = False
        elif snake2:
            snake2.shrink()

        # Spawn new food if needed
        if not food_spawn:
            food_position = spawn_food_with_safe_zone(snake1.body, snake2.body if snake2 else [])
            food_spawn = True

        # Check for collisions
        handle_collisions(snake1, snake2, green_score, blue_score)

        # Clear the screen
        screen.fill(BLACK)

        # Draw the snakes and food
        snake1.draw(screen)
        if snake2:
            snake2.draw(screen)
        draw_food(food_position)

        # Display the scores
        if snake2:
            display_score(green_score, blue_score)
        else:
            display_score(green_score, 0)

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        clock.tick(36)  # Increase frame rate FPS


def handle_collisions(snake1, snake2, green_score, blue_score):
    """Handle all collision scenarios."""
    # Self-collision for Green Snake
    if snake1.collides_with_self():
        end_game(snake2, green_score, blue_score)

    # Self-collision for Blue Snake
    if snake2 and snake2.collides_with_self():
        end_game(snake2, green_score, blue_score)

    # Collision between Green and Blue
    if snake2 and (snake1.collides_with(snake2) or snake2.collides_with(snake1)):
        end_game(snake2, green_score, blue_score)


def end_game(snake2, green_score, blue_score):
    """Determine the winner and display the result."""
    if green_score > blue_score:
        display_result("Green Wins!", green_score, blue_score)
    elif blue_score > green_score:
        display_result("Blue Wins!", green_score, blue_score)
    else:
        display_result("It's a draw!", green_score, blue_score)
    sys.exit()


def display_result(result_text, green_score, blue_score):
    """Display the result of the game on the screen along with the scores."""
    screen.fill(BLACK)  # Clear the screen
    result_font = pygame.font.SysFont("arial", 50)  # Larger font for the result
    result_surface = result_font.render(result_text, True, WHITE)
    screen.blit(result_surface, [SCREEN_WIDTH // 2 - result_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 100])

    # Display the scores
    score_font = pygame.font.SysFont("arial", 40)
    score_surface = score_font.render(f"Green: {green_score}  Blue: {blue_score}", True, WHITE)
    screen.blit(score_surface, [SCREEN_WIDTH // 2 - score_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 30])

    # Display instructions to return to the menu
    instruction_font = pygame.font.SysFont("arial", 25)
    instruction_surface = instruction_font.render("Press any key to return to the menu", True, WHITE)
    screen.blit(instruction_surface, [SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2, SCREEN_HEIGHT // 2 + 50])

    pygame.display.flip()  # Update the display

    # Wait for the user to press a key
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return  # Return to the menu


if __name__ == "__main__":
    menu()