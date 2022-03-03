from turtle import width
import pygame
import numpy as np
import gym
import random
import math


FPS = 60
WIDTH, HEIGHT = 1200, 800
MAX_RP, MAX_ACC = 1, 1

# colors
BLOOD = (247, 209, 209)
RED = (250, 10, 100)
GREY = (128, 128, 128)

RADIUS = 100
STEM = [[WIDTH - 30, 30], [WIDTH-30, HEIGHT-30]]
e = 0.5
NUM_BOTS = 50
NUM_TUMOR = 20
NUM_RBC = 200
NUM_STEM = 2

# images
Bot_img = pygame.image.load('bott.png')
Bot_img_copy = pygame.transform.rotate(Bot_img, 270)
tumor_img = pygame.image.load(
    "tumor_3.png")
rbc_image = pygame.image.load(
    "rbc_3.png")


class Bot():
    def __init__(self, id):
        self.id = id
        self.pos = [random.uniform(80, 120), random.uniform(80, 120)]
        self.vel = [0, 0]
        self.ang_acc = 0
        self.angle = 0
        self.observ = []
        self.r = 12

    def update(self, action):

        # Do nothing
        if (action == 0):
            pass

        # Accelaration
        if (action == 1):
            self.vel[0] = self.vel[0] + MAX_ACC * np.cos(self.ang_acc)
            self.vel[1] = self.vel[1] - MAX_ACC * np.sin(self.ang_acc)

        # Retardation
        if (action == 2):
            self.vel[0] = self.vel[0] - MAX_ACC * np.cos(self.ang_acc)
            self.vel[1] = self.vel[1] + MAX_ACC * np.sin(self.ang_acc)

        # Rotate left
        if (action == 3):
            self.ang_acc = self.ang_acc + MAX_RP
            if self.ang_acc > np.pi:
                self.ang_acc = self.ang_acc - 2 * np.pi
            if self.ang_acc < -np.pi:
                self.ang_acc = self.ang_acc + 2 * np.pi
        # Rotate Right
        if (action == 4):
            self.ang_acc = self.ang_acc - MAX_RP
            if self.ang_acc > np.pi:
                self.ang_acc = self.ang_acc - 2 * np.pi
            if self.ang_acc < -np.pi:
                self.ang_acc = self.ang_acc + 2 * np.pi

        # move bot
        self.pos[0] = self.pos[0] + self.vel[0]
        self.pos[1] = self.pos[1] + self.vel[1]

        # keep bot on screen (optional)
        if self.pos[0] > WIDTH - 10:
            self.pos[0] = WIDTH - 10
        elif self.pos[0] < 10:
            self.pos[0] = 10
        if self.pos[1] > HEIGHT - 10:
            self.pos[1] = HEIGHT - 10
        elif self.pos[1] < 10:
            self.pos[1] = 10

        # Moving Angle
        if (self.vel[0] > 0):
            if(self.vel[1] < 0):
                self.angle = 360 + \
                    math.degrees(math.atan(self.vel[1]/self.vel[0]))
            else:
                self.angle = math.degrees(math.atan(self.vel[1]/self.vel[0]))
        elif (self.vel[0] < 0):
            self.angle = 180 + math.degrees(math.atan(self.vel[1]/self.vel[0]))
        else:
            if self.vel[1] > 0:
                self.angle = 90
            else:
                self.angle = 270

        # print(self.angle)

    def reset(self):
        self.ang_acc = 0
        self.vel = [0, 0]
        self.pos = [random.uniform(80, 120), random.uniform(80, 120)]


class RBC():
    def __init__(self):
        # self.id=id
        self.pos = [random.uniform(-WIDTH, WIDTH),
                    random.uniform(-HEIGHT, HEIGHT)]
        self.vel = [random.uniform(0.5, 2),
                    random.uniform(0.5, 2)]
        self.r = 10

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] -= self.vel[1]

        if self.pos[1] < 0 or self.pos[0] > WIDTH:
            self.vel = [random.uniform(1, 2),
                        random.uniform(1, 2)]
            self.pos = [random.uniform(-WIDTH, 0),
                        random.uniform(HEIGHT, 2*HEIGHT)]
        if self.vel[0] < 1:
            self.vel[0] += 0.1
        if self.vel[1] < 1:
            self.vel[1] += 0.1


class tumor():
    def __init__(self, s):
        self.id = s
        self.stem = STEM[s]
        self.pos = [STEM[s][0], STEM[s][1]]  # [STEM[0], STEM[1]]
        self.vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.r = 15

        self.stem_vel = [random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)]

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] *= 1.01
        self.vel[0] *= 1.01

        # stem movement
        self.stem[0] += self.stem_vel[0]
        self.stem[1] += self.stem_vel[1]
        if self.stem[0] > WIDTH or self.stem[0] < WIDTH - 30:
            self.stem_vel[0] *= -1
        if self.stem[1] < 0 or self.stem[1] > HEIGHT:
            self.stem_vel[1] *= -1
        #self.r += ((math.sqrt(math.pow((STEM[0] -self.pos[0]), 2)+math.pow((STEM[1] - self.pos[1]), 2)))) / (RADIUS)
        # if self.r > 7:
        #self.r = 7


class CustomEnv(gym.Env):
    def __init__(self):
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=(1200, 800, 3), dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(5)
        self.num_bots = NUM_BOTS
        self.agents = [Bot(i) for i in range(self.num_bots)]
        self.num_stem = NUM_STEM
        self.num_tumor = NUM_TUMOR
        self.tumor = []
        for s in range(self.num_stem):
            for i in range(self.num_tumor):
                self.tumor.append(tumor(s))
        self.num_rbc = NUM_RBC
        self.rbc = [RBC() for i in range(self.num_rbc)]
        self.count = 0
        self.MAX_STEPS = 999
        self.done = False

    # START RENDER
    def init_render(self):
        import pygame
        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

    # RESET
    def reset(self):
        self.init_render()
        self.nanobot.reset()
        self.done = False
        self.observation = np.array(pygame.surfarray.array3d(self.window))
        self.count = 0
        return self.observation

    # STEP
    def step(self, action):
        # np.array(pygame.surfarray.array3d(self.window))

        self.reward = -50
        self.done = False
        self.info = {}
        for i, agent in enumerate(self.agents):
            agent.update(action[i])

        # collisions
            # between bots
        for a in self.agents:
            for b in self.agents:
                if b is a:
                    continue
                else:
                    if is_collision(self, a, b):
                        self.reward -= 1
                        collide(a, b, e)
        # between rbcs
        for a in self.rbc:
            for b in self.rbc:
                if b is a:
                    continue
                else:
                    if is_collision(self, a, b):
                        self.reward -= 10
                        collide(a, b, e)
            # between bots and tumor
        for a in self.agents:
            for b in self.tumor:
                if is_collision(self, a, b):
                    collide(a, b, e)
            # between bots and rbc
        for a in self.agents:
            for b in self.rbc:
                if is_collision(self, a, b):
                    collide(a, b, e)
            # between rbc and tumor
        for a in self.rbc:
            for b in self.tumor:
                if is_collision(self, a, b):
                    collide(a, b, e)

        # observation space
        self.observation = []

        # Agents position
        agent_pos = []
        for a in self.agents:
            agent_pos.append(a.pos)

        # Agents veclocity
        agent_vel = []
        for agent in self.agents:
            agent_vel.append(agent.vel)

        # Other agents relative postition
        relative_agent_pos_list = []
        for a in self.agents:
            relative_agent_pos = []
            for b in self.agents:
                if a is b:
                    continue
                else:
                    relative_agent_pos.append(
                        [b.pos[0]-a.pos[0], b.pos[1]-a.pos[1]])
            relative_agent_pos_list.append(relative_agent_pos)

        # RBC's relative positiion
        relative_rbc_pos_list = []
        for a in self.agents:
            relative_rbc_pos = []
            for b in self.rbc:
                relative_rbc_pos.append([b.pos[0]-a.pos[0], b.pos[1]-a.pos[1]])
            relative_rbc_pos_list.append(relative_rbc_pos)

        # Tumor's relative posistion
        relative_tumor_pos_list = []
        for a in self.agents:
            relative_tumor_pos = []
            for b in self.tumor:
                relative_tumor_pos.append(
                    [b.pos[0]-a.pos[0], b.pos[1]-a.pos[1]])
            relative_tumor_pos_list.append(relative_tumor_pos)

        # Creating the overall state of the env
        for i in range(NUM_BOTS):
            self.observation.append(agent_pos[i])
            self.observation.append(agent_vel[i])
            self.observation.append(relative_agent_pos_list[i])
            self.observation.append(relative_rbc_pos_list[i])
            self.observation.append(relative_tumor_pos_list[i])

        # for tumor group
        for t in self.tumor:
            t.update()
            id = t.id
            if(math.sqrt(math.pow((t.stem[0] - t.pos[0]), 2)+math.pow((t.stem[1] - t.pos[1]), 2)) > RADIUS):
                self.tumor.remove(t)
                self.tumor.append(tumor(id))

        # for rbc group
        for r in self.rbc:
            r.update()

        self.count += 1
        self.render()
        if (self.reward > -30):
            self.done = True
        if self.count > self.MAX_STEPS:
            self.done = True
        return self.observation, self.reward, self.done, self.info

    # RENDER
    def render(self):
        self.window.fill(BLOOD)
        for agent in self.agents:
            img = pygame.transform.rotate(Bot_img_copy, - agent.angle)
            self.window.blit(img, agent.pos)
        for tumor in self.tumor:
            self.window.blit(tumor_img, tumor.pos)
        for rbc in self.rbc:
            self.window.blit(rbc_image, rbc.pos)
        pygame.display.update()


def is_collision(self, agent1, agent2):
    dx, dy = agent1.pos[0] - agent2.pos[0], agent1.pos[1] - agent2.pos[1]
    d = math.sqrt(dx**2 + dy**2)
    return True if d < agent2.r + agent1.r else False


def collide(self, agent, elasticity):
    dx, dy = self.pos[0] - agent.pos[0], self.pos[1] - agent.pos[1]
    d = math.sqrt(dx**2 + dy**2)
    if d == 0:
        d = 0.1
    dvx, dvy = self.vel[0] - agent.vel[0], self.vel[1] - agent.vel[1]

    sin, cos = dx/d, dy/d
    dr = (self.r + agent.r - d) / 2
    dx2, dy2 = sin * dr, cos * dr

    self.pos[0] += dx2
    self.pos[1] += dy2
    agent.pos[0] -= dx2
    agent.pos[1] -= dy2

    h = (dx * dvx + dy * dvy) / d
    new_dvx, new_dvy = -h * sin * elasticity, -h * cos * elasticity

    self.vel[0] += new_dvx
    self.vel[1] += new_dvy
    agent.vel[0] -= new_dvx
    agent.vel[1] -= new_dvy


env = CustomEnv()
env.init_render()

while not env.done:
    env.clock.tick(FPS)
    get_event = pygame.event.get()
    for event in get_event:
        if event.type == pygame.QUIT:
            env.done = True
    action = np.random.randint(4, size=env.num_bots)
    env.step(action)
    # render current state
    env.render()
pygame.quit()
