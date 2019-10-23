
class Node:
    def __init__(self, name):
        self.name = name 
        self.neighbors = []
        self.color = 0
        self.live_neighbor_size = 0

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
        if not neighbor.spilled():
            self.live_neighbor_size += 1

    def neighbor_size(self):
        return len(self.neighbors)

    def spilled(self):
        return self.color < 0

    def spill(self):
        self.color = -1;
        for each in self.neighbors:
            each.live_neighbor_size -= 1

    def colored(self):
        return self.color > 0

    def assign_color(self, k):
        used = []
        for each in self.neighbors:
            if each.colored():
                used.append(each.color)

        for c in range(k):
            if (c+1) not in used:
                self.color = c+1
                break

        if self.colored():
            return True
        return False

    def validate(self):
        if self.colored():
            for each in self.neighbors:
                if each.colored() and each.color == self.color:
                    print(self.color, each.color)
                    return False
            return True
        elif self.spilled():
            return True
        return False

            
def optimistic_coloring(nodes, k): 
    colored = []
    spilled = []

    while len(nodes) > 0:
        min_value = nodes[0].live_neighbor_size
        min_index = 0
        for i in range(1, len(nodes)):
            if nodes[i].live_neighbor_size < min_value:
                min_value = nodes[i].live_neighbor_size
                min_index = i

        if nodes[min_index].assign_color(k):
            colored.append(nodes[min_index])
        else:
            nodes[min_index].spill()
            spilled.append(nodes[min_index])
        nodes = nodes[:min_index] + nodes[min_index+1:]

    return colored, spilled

def add_edge(left, right):
    left.add_neighbor(right)
    right.add_neighbor(left)
