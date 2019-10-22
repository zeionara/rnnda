import numpy as np

batch_names = ['train', 'val', 'test']
batch_proportions = [0.7, 0.2, 0.1]
resource_dir = 'viot_data/'

main_file_path = resource_dir + "all_text.txt"

with open(main_file_path, "r") as file:
	lines = file.readlines()

number_of_lines = len(lines)
boundaries = [int(np.sum(batch_proportions[:i + 1]) * number_of_lines) for i in range(len(batch_proportions) - 1)]
np.random.shuffle(lines)
splitted = np.split(lines, boundaries)

for i in range(len(batch_names)):
	batch_name = batch_names[i]
	file_path = resource_dir + batch_name + "_text.txt"
	with open(file_path, "w+") as file:
		file.writelines(splitted[i])