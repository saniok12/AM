from analysis import data_collection_mode
from simulation import interactive_mode

def main():
    print("Select mode:")
    print("1. Interactive simulation")
    print("2. Data Analysis")
    mode = input("Enter your choice (1 or 2): ")

    if mode == "2":
        data_collection_mode()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
