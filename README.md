# recordatorioSQL

This package is to get my reminders in my virtual assistant. Most of them being birthdays.  
  
I used to do this with **JSON**, but converted it to **SQL** to make it more reliable.


## Usage
  
This is one of my most used functions of my virtual assistant. It runs in a Raspberry Pi, that is not powerfull enough to run Artificial Intelligence models; and Natural Language in Spanish do not work as very well, so I've tryed to make it the most naturallanguaged as possible.  
It keeps the reminders and everyday it checks if there's something scheduled. Then it sends it to the user (just me for now), few times during the day until posted as completed or deleted. It also checks for reminders the night before, and one week before. So it would tell you "_reminder in one week: Cecilia’s Birthday_".  

### Callings
So you first ask for something by calling:
```python
import recordat

recordat.orio(chat_id = 7654321, vaina = '<<request here>>')
```
The word _Recordatorio_ means _Reminder_, hence the name. 
The **request** might be one of many options:
If you want to check at your reminders you can ask for them as:

- Dame mis recordatorios - (_Give me my reminders_).
- Me dariás mis recordatorios - (_Would you give me my reminders_).
- Muestrane mis recordatorios - (_Show me my reminders_).
- Mandame mis recordatorios - (_Send me my reminders_).

Just showing how it consider differents words and conjugations.

You can also specify the month you want:
- Dame mis recordatorios de abril - (_Give me my reminders of April_).

That would be something like:
```python
print(recordat.orios(7654321, "dame mis recordatorios de abril")
```
```markdown
# output
• APRIL •
02 - License paperwork
   - Get groceries
14 - Jerry's Birthday
23 - Dinner with family
```


## Features

- **SQL**: Very fast.
- **Fuzzy Searcher**: Don’t worry about small misspellings.
- **Time Left**: How long until your special date.
- **Spanish Verbs Conjugation Considerer**: Spanish, opposite than English, has many ways of verbs conjugatios. Here we consider that.
- **Week Days**: You can say "_reminder next Thursday this and that_".

## Contributions

Contributions are welcome! If you have improvements or fixes, please send a pull request or open an issue in the GitHub repository.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details. Use it as you like.

## Contact

Nico Spok - nicospok@proton.me
GitHub: niCodeLine
