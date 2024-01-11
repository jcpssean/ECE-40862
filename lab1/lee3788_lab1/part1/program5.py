def find_pair(nums, target):
    seen = {}
    for idx, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            print(f"index1={seen[diff]}, index2={idx}")
            return
        seen[n] = idx
    print(f"Can't find a pair to sum up to {target}")

numbers = [10, 20, 10, 40, 50, 60, 70]
target = int(input("What is your target number? "))

find_pair(numbers, target)