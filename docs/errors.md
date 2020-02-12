# Error Codes (BHIVE::ERROR)
0: Reserved
1: Invalid number of parameters passed
2: Invalid function

# Pollen Codes (POLLEN::ERROR)
0: Unexpected End of File
1: Unexpected end of bracket ")"

If you're receiving "None" or invalid behaviour back from a Pollen script, check that you've ended your individual statements with a semicolon, otherwise it will parse one statement then stop, returning whatever is processed on the first line.