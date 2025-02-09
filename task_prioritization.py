import numpy as np
import random

class TaskScheduler:
    def __init__(self, tasks, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.1):
        self.tasks = tasks  # List of tasks
        self.q_table = {task: np.zeros(len(tasks)) for task in tasks}  # Q-table
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

    def choose_task(self, current_task):
        if random.uniform(0, 1) < self.exploration_rate:
            return random.choice(self.tasks)  # Explore
        else:
            return self.tasks[np.argmax(self.q_table[current_task])]  # Exploit

    def update_q_value(self, current_task, next_task, reward):
        best_next_q = np.max(self.q_table[next_task])
        self.q_table[current_task][self.tasks.index(next_task)] += self.learning_rate * (
            reward + self.discount_factor * best_next_q - self.q_table[current_task][self.tasks.index(next_task)]
        )

    def simulate_user_feedback(self, task):
        return np.random.choice([-1, 0, 1], p=[0.2, 0.5, 0.3])  # Randomized reward

    def train(self, iterations=1000):
        for _ in range(iterations):
            current_task = random.choice(self.tasks)
            next_task = self.choose_task(current_task)
            reward = self.simulate_user_feedback(next_task)
            self.update_q_value(current_task, next_task, reward)

    def get_optimal_schedule(self):
        return sorted(self.tasks, key=lambda t: np.max(self.q_table[t]), reverse=True)


# Example tasks
tasks = ["Email", "Meeting", "Coding", "Testing", "Documentation"]

# Initialize scheduler
scheduler = TaskScheduler(tasks)
scheduler.train()

# Get optimized task order
optimal_schedule = scheduler.get_optimal_schedule()
print("Optimized Task Schedule:", optimal_schedule)
