from pathlib import Path
import re
import random

#No need to mess w/ this stuff, patterns pull from the formatted files
BASE_DIR = Path(__file__).resolve().parent
QUESTION_PATTERN = re.compile(r"^#{1,6}\s*(\d+)\.\s*(.+?)\s*$")
OPTION_PATTERN = re.compile(r"^([A-D])\.\s*(.+?)\s*$", re.I)
ANSWER_PATTERN = re.compile(r"^(\d+)\.\s*([A-D])\b", re.I)


def choose_quiz():
	# Display the available question files and let the user choose one.
	quiz_files = sorted(
		(path for path in BASE_DIR.glob("*.md") if "questions" in path.stem.casefold()),
		key=lambda path: path.stem.casefold(),
	)
	if not quiz_files:
		return None
	# If only one quiz is available, select it without asking.
	if len(quiz_files) == 1:
		return quiz_files[0]

	# Show a numbered menu of all available quiz files.
	print("Choose a quiz:")
	for number, path in enumerate(quiz_files, start=1):
		print(f"{number}. {path.stem}")

	# Keep asking until the user enters a valid quiz number.
	while True:
		response = input("Quiz number: ").strip()
		if response.isdigit():
			index = int(response) - 1
			if 0 <= index < len(quiz_files):
				return quiz_files[index]
		print("Invalid selection.")


def load_quiz(path):
	# Read questions, multiple-choice options, and answer-key entries from a Markdown file.
	lines = path.read_text(encoding="utf-8-sig").splitlines()
	answers = {}
	questions = []
	current = None
	in_answer_key = False

	for line in lines:
		stripped = line.strip().strip("*")
		# Match headings so answer-key sections can be identified.
		heading = re.match(r"^#{1,6}\s*(.+?)\s*$", stripped)
		section_name = heading.group(1).casefold() if heading else ""
		if heading and ("answer key" in section_name or "answer sheet" in section_name):
			in_answer_key = True
			continue

		# Store numbered answers while processing the answer-key section.
		answer_match = ANSWER_PATTERN.match(stripped)
		if in_answer_key and answer_match:
			answers[int(answer_match.group(1))] = answer_match.group(2).upper()
			continue

		# Start a new question when a numbered heading is found.
		question_match = QUESTION_PATTERN.match(line.strip())
		if question_match:
			current = {
				"number": int(question_match.group(1)),
				"text": question_match.group(2).strip("* "),
				"options": [],
			}
			questions.append(current)
			continue

		# Add A-D answer choices to the current question.
		option_match = OPTION_PATTERN.match(line.strip())
		if current is not None and option_match:
			current["options"].append(
				(option_match.group(1).upper(), option_match.group(2).strip("* "))
			)

	# Only include questions that have a corresponding answer-key entry.
	usable = []
	for question in questions:
		answer = answers.get(question["number"])
		if answer:
			usable.append({**question, "answer": answer})
	return usable


def is_correct(response, question):
	# Check whether a user's response matches a question's answer letter or option text.
	response = response.strip().casefold()
	answer = question["answer"].casefold()
	for label, text in question["options"]:
		if label.casefold() == answer:
			return response in {label.casefold(), text.casefold()}
	return False


def main():
	# Run quiz selection, ask up to five random questions, and show the final score.
	question_file = choose_quiz()
	if question_file is None:
		print("No quiz .md files with 'Questions' in the name were found.")
		return

	questions = load_quiz(question_file)
	if not questions:
		print(f"No usable questions found in {question_file.name}.")
		return

	correct = 0
	print(f"\n{question_file.stem} quiz\n")
	# Randomly select up to five unique questions.
	quiz_questions = random.sample(questions, min(5, len(questions)))
	for number, question in enumerate(quiz_questions, start=1):
		print(f"{number}. {question['text']}")
		# Display each available answer choice.
		for label, text in question["options"]:
			print(f"   {label}. {text}")

		response = input("Your answer: ").strip()
		# Compare the response with the answer key and update the score.
		if is_correct(response, question):
			correct += 1
			print("Correct!\n")
		else:
			print(f"Incorrect. Correct answer: {question['answer']}\n")

	print(f"Results: {correct} correct, {len(quiz_questions) - correct} incorrect.")


if __name__ == "__main__":
	main()
