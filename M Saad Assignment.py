s = input("Enter a string: ")

letters = digits = special = 0
for ch in s:
    if ch.isalpha():
        letters += 1
    elif ch.isdigit():
        digits += 1
    else:
        special += 1

print("Letters:", letters)
print("Digits:", digits)
print("Special characters:", special)

##Numbers Divisible by 4 or 6 (But Not Both)

start = int(input("Enter start: "))
end = int(input("Enter end: "))

for i in range(start, end + 1):
    if (i % 4 == 0 or i % 6 == 0) and not (i % 4 == 0 and i % 6 == 0):
        print(i, end=" ")

#Count Uppercase and Lowercase Letters

s = input("Enter a sentence: ")

upper = lower = 0
for ch in s:
    if ch.isupper():
        upper += 1
    elif ch.islower():
        lower += 1

print("Uppercase letters:", upper)
print("Lowercase letters:", lower)

###Replace Vowels with ‘*’

word = input("Enter a word: ")
vowels = "aeiouAEIOU"

for v in vowels:
    word = word.replace(v, '*')

print("After replacement:", word)


###Find Sum of Numbers Entered in a String

s = input("Enter a string: ")

total = 0
for ch in s:
    if ch.isdigit():
        total += int(ch)

print("Sum of digits:", total)

##Count Words Starting with a Vowel

sentence = input("Enter a sentence: ")
vowels = "aeiouAEIOU"

words = sentence.split()
count = 0

for word in words:
    if word[0] in vowels:
        count += 1

print("Words starting with a vowel:", count)

##Display Numbers with Sum of Digits Even


start = int(input("Enter start: "))
end = int(input("Enter end: "))

for i in range(start, end + 1):
    digit_sum = sum(int(d) for d in str(i))
    if digit_sum % 2 == 0:
        print(i, end=" ")

#Character Frequency (Sorted)

s = input("Enter a string: ")

freq = {}
for ch in s:
    freq[ch] = freq.get(ch, 0) + 1

for ch in sorted(freq.keys()):
    print(f"{ch}: {freq[ch]}")

#Numbers Having 3 as a Digit

start = int(input("Enter start: "))
end = int(input("Enter end: "))

for i in range(start, end + 1):
    if '3' in str(i):
        print(i, end=" ")

##Complex Divisibility with Digit Logic

start = int(input("Enter start: "))
end = int(input("Enter end: "))

for i in range(start, end + 1):
    sum_digits = sum(int(d) for d in str(i))
    if ((i % 4 == 0 or i % 6 == 0) and not (i % 4 == 0 and i % 6 == 0)
        and sum_digits % 2 != 0 and i % 9 != 0):
        print(i, end=" ")


