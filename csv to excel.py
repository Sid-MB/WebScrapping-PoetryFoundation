from fileinput import filename
import pandas as pd

fileName = "results/poems 08-30-2022 15:28:54.csv"
df = pd.read_csv(fileName)

print(df.head())

# getting first two and last two
def first_two(content: str) -> str:
	if not isinstance(content, str):
		return first_two(str(content))

	lines = list(map(lambda x: x.strip(), content.split("\n")))
	lines = [l for l in lines if ("✷" not in l)]
	lines = [l for l in lines if l]  # remove empty lines

	if len(lines) < 2:
		return "nan"
	
	return "  /  ".join(lines[0:2]).strip()

def last_two(content: str) -> str:
	if not isinstance(content, str):
		return last_two(str(content))

	lines = list(map(lambda x: x.strip(), content.split("\n")))
	lines = [l for l in lines if ("✷" not in l)]
	lines = [l for l in lines if l]  # remove empty lines

	if len(lines) < 2:
		return "nan"

	return "  /  ".join(lines[-2:]).strip()

df['first-line'] = df['content'].map(first_two)
df['last-line'] = df['content'].map(last_two)

df.drop(['content'], axis=1, inplace=True)
df.dropna(inplace=True)

df = df[(df['first-line'] != "/") & (df['last-line'] != "/")]  # type: ignore
# & ("✷" not in df['last-line'])

df = df[(df['first-line'] != "nan") & (df['last-line'] != "nan")]

print(df.sample(5))
df.to_excel(fileName + ".trimmedlines.xlsx", index=False)