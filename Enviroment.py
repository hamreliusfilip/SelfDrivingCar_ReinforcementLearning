import pygame
from settings import *
from bus import Bus

class BusEnvironment:
    def __init__(self, screen, bus):
        self.screen = screen
        self.bus = bus  # Store the bus object
        track = pygame.image.load('final_track.png')
        self.image = pygame.transform.scale(track, (WIDTH, HEIGHT))
        self.contour_points = BARRIERS
        self.checkpoints = CHECKPOINTS

        # List to keep track of whether each checkpoint has been passed
        self.checkpoint_passed = [False] * len(self.checkpoints)

        self.VIS_BARRIERS = True
        self.VIS_CHECKPOINTS = True
        
        # Smiley faces
        self.happy_smiley = pygame.image.load('happy.png')  # Lägg till sökväg till din glad smiley
        self.sad_smiley = pygame.image.load('sad.png')      # Lägg till sökväg till din ledsen smiley
        self.smiley_size = (65, 65)  # Storleken på smileyn
        
    def draw(self):
        self.screen.blit(self.image, (0, 0))
       
        # if self.VIS_BARRIERS:
        #     self.draw_barriers()
        # if self.VIS_CHECKPOINTS:
        #     self.draw_checkpoints()
        
        # Visa hastigheten i det övre högra hörnet
        speed_text = pygame.font.Font(None, 30).render(f"Fart: {12.5 * self.bus.velocity:.2f} km/h", True, (0, 0, 0))
        self.screen.blit(speed_text, (WIDTH - 170, 10))  # Display speed at top-right corner
        
        # Draw the bus on the screen
        self.bus.update()
        self.bus.draw(self.screen)
        self.draw_smiley()

        # Check if the bus passed any checkpoints
        self.update_checkpoints()
        
    def draw_smiley(self):
        # Position och storlek för den rektangulära rutan
        box_width = 120
        box_height = 100
        box_pos_x = WIDTH - box_width - 10  # Justera så att den är lite in från kanten
        box_pos_y = 60  # Justera vertikalt

        # Definiera färger
        border_color = (0, 0, 0)  # Svart färg för kanten
        fill_color = (200, 200, 200)  # Ljusgrå bakgrund för att simulera en digital skylt

        # Rita rektangeln med en ljusgrå bakgrund och rundade hörn
        radius = 10  # Radie för hörnen
        pygame.draw.rect(self.screen, fill_color, (box_pos_x, box_pos_y, box_width, box_height), 0, radius)  # Ljusgrå rektangel med rundade hörn

        # Rita kantlinjen (svart) runt rektangeln med samma radie
        pygame.draw.rect(self.screen, border_color, (box_pos_x, box_pos_y, box_width, box_height), 5, radius)  # Svart rektangel med rundade hörn

        # Rita texten "Din Fart" i rektangeln
        font = pygame.font.Font(None, 30)
        text = font.render("Din Fart", True, (0, 0, 0))  # Svart text
        text_rect = text.get_rect(center=(box_pos_x + box_width // 2, box_pos_y + 20))  # Centrera texten ovanför smileyn
        self.screen.blit(text, text_rect)

        # Kontrollera om bussen är i skolzon
        # in_school_zone = self.is_in_school_zone()

        # Bestäm smileyn baserat på hastighet och om bussen är i skolzon
        if self.bus.schoolzone[self.bus.checkpoint_index] == 1:  # Om bussen är i skolzonen
            if self.bus.velocity < 2:  # Skolzon och hastigheten är under 2
                smiley_image = pygame.transform.scale(self.happy_smiley, self.smiley_size)  # Glad smiley
            else:  # För snabb i skolzonen
                smiley_image = pygame.transform.scale(self.sad_smiley, self.smiley_size)  # Ledsen smiley
        else:
            if self.bus.velocity > 2:  # Inte i skolzon och hastigheten är över 2
                smiley_image = pygame.transform.scale(self.happy_smiley, self.smiley_size)  # Glad smiley
            else:  # För långsam utanför skolzonen
                smiley_image = pygame.transform.scale(self.sad_smiley, self.smiley_size)  # Ledsen smiley

        # Placera smileyn i mitten av rektangeln, justera vertikalt
        smiley_pos_x = box_pos_x + (box_width - self.smiley_size[0]) // 2  # Centrera smileyn horisontellt
        smiley_pos_y = box_pos_y + (box_height - self.smiley_size[1]) // 2 + 10  # Centrera smileyn vertikalt, justera för texten

        # Rita smileyn
        self.screen.blit(smiley_image, (smiley_pos_x, smiley_pos_y))

    def draw_barriers(self):
        pygame.draw.lines(self.screen, (255, 0, 0), True, self.contour_points[0], 5)
        pygame.draw.lines(self.screen, (255, 0, 0), True, self.contour_points[1], 5)
        for point in np.vstack(self.contour_points):
            pygame.draw.circle(self.screen, (0, 0, 255), point, 5)
            
    def draw_checkpoints(self):
        for index, checkpoint in enumerate(self.checkpoints):
            # Determine the color based on whether the checkpoint has been passed
            if index == 0:
                # Start checkpoint
                pygame.draw.line(self.screen, (0, 255, 0), (checkpoint[0], checkpoint[1]), (checkpoint[2], checkpoint[3]), 3)
                self.screen.blit(pygame.font.Font(None,30).render(f"START", True, (0,255,0)), ((checkpoint[0] - 30, checkpoint[1] - 50)))
            else:
                color = (255, 255, 0) if self.checkpoint_passed[index] else (255, 0, 0)
                pygame.draw.line(self.screen, color, (checkpoint[0], checkpoint[1]), (checkpoint[2], checkpoint[3]), 3)

    def update_checkpoints(self):
        """Check if the bus passed a checkpoint and update the list."""
        checkpoint_threshold = 50  # Threshold distance to consider a checkpoint as "passed"
        bus_position = pygame.math.Vector2(self.bus.rect.center)

        # Loop through checkpoints and check if the bus passed any
        for index, checkpoint in enumerate(self.checkpoints):
            if not self.checkpoint_passed[index]:  # Only check checkpoints not yet passed
                checkpoint_position = pygame.math.Vector2((checkpoint[0] + checkpoint[2]) // 2, (checkpoint[1] + checkpoint[3]) // 2)
                if bus_position.distance_to(checkpoint_position) < checkpoint_threshold:
                    self.checkpoint_passed[index] = True
                    if index == len(self.checkpoints) - 1:
                        self.reset_checkpoints()   # Reset after last checkpoint
                        self.bus.laps_completed += 1

    def reset_checkpoints(self):
        """Reset all checkpoints to the unpassed state (all red)."""
        self.checkpoint_passed = [False] * len(self.checkpoints)
