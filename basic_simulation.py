from world import World

def main():
	my_world = World(50, 0.05, 1, reproduction_mutation_chance=0)

	for i in range(150):
		my_world.pass_day(100)
		if my_world.days_passed < 21 or my_world.days_passed%10 == 0:
			my_world.show_me(save_plot=True)
		print("days_passed: ", my_world.days_passed,
			" creatures: ", len(my_world.creatures))
	my_world.plot_history(save_plot=True)

if __name__ == "__main__":
	main()