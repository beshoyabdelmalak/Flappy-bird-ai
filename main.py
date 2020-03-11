import pygame
import os
import time
import neat
from model import Bird, Base, Pipe

pygame.font.init()
GENERATION = 0
WN_WIDTH = 500
WN_HIGHT = 800
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

STAT_FONT = pygame.font.SysFont('comicsans', 50)

def draw_window(window, birds, base, pipes, score, gen):
	window.blit(BG_IMG, (0,0))

	for pipe in pipes:
		pipe.draw(window)
	
	score = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
	window.blit(score, (WN_WIDTH - 10  - score.get_width(), 10))

	generation = STAT_FONT.render("Geration: " + str(gen), 1, (255,255,255))
	window.blit(generation, (10, 10))

	base.draw(window)
	for bird in birds:
		bird.draw(window)

	pygame.display.update()


def main(genomes, config):
	global GENERATION
	GENERATION +=1
	genome = []
	nets = []
	birds = []
	pipes = [Pipe(600)]
	base = Base(730)

	for _, g in genomes:
		g.fitness = 0.0  # start with fitness level of 0
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(230,350))
		genome.append(g)


	window = pygame.display.set_mode((WN_WIDTH, WN_HIGHT))
	pygame.display.set_caption('Flappy Bird')
	clock = pygame.time.Clock()
	score = 0
	
	run = True
	# start = True
	# e = True
	while run:
		clock.tick(40)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
		if len(birds) == 0:
			break


		for i,bird in enumerate(birds):
			next_pipe = 0
			if bird.x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				next_pipe = 1
			bird.move()
			genome[i].fitness += 0.1
			result = nets[i].activate((bird.y, abs(bird.y - pipes[next_pipe].height), abs(bird.y - pipes[next_pipe].bottom)))
			if result[0] > 0.5:
				bird.jump()
			
			if base.collide(bird):
				genome[i].fitness -= 1
				birds.pop(i)
				nets.pop(i)
				genome.pop(i)
				continue

			remove_pipes = []
			passed = False
			crashed = False

			for pipe in pipes:
				if pipe.collide(bird):
					genome[i].fitness -= 1
					birds.pop(i)
					nets.pop(i)
					genome.pop(i)
					crashed = True
				
				if pipe.x + pipe.PIPE_TOP.get_width() < 0:
					remove_pipes.append(pipe)

				if not pipe.passed and pipe.x < bird.x:
					pipe.passed = True
					passed = True

			if crashed:
				continue
			# if the bird passed the pipe increment score and add new pipe
			if passed:
				genome[i].fitness += 1
				score += 1
				pipes.append(Pipe(600))
			
			# delete pipes that are out of the screen
			for remove in remove_pipes:
				pipes.remove(remove)

			# check if the bird hit the ground
			if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
				genome[i].fitness -= 1
				birds.pop(i)
				nets.pop(i)
				genome.pop(i)
				continue
		
		for pipe in pipes:
			pipe.move()
		base.move()
		draw_window(window, birds, base, pipes, score, GENERATION)


def play_ai(config_path):
	config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
	p = neat.Population(config)
	
	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)
	p.add_reporter(neat.Checkpointer(5))

	winner = p.run(main, 10)

	# Display the winning genome.
	print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir, 'config.txt')
	play_ai(config_path)