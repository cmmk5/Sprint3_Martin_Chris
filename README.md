# CS449 Solitaire Sprint 3

Chris Martin

## Run the game

Use Python 3.10 or later with Tkinter. Open a terminal in the extracted
Sprint3 folder and run:

```powershell
python gui.py
python -m unittest discover -s tests -v
```

In Visual Studio 2022, you can also set gui.py as the startup file.

Choose English, Hexagon, or Diamond and size 5, 7, or 9. Selecting a
board type immediately starts a game. To apply a size change on its own,
click New Game. Click a peg, then click an empty destination. A valid
jump removes the peg in between. The status shows the rating when no
legal jumps remain. Undo restores the previous position.

For a short manual demo, choose English size 5. With zero-based
(row, column) coordinates, play these jumps in order:

1. (0, 2) to (2, 2)
2. (3, 2) to (1, 2)
3. (2, 0) to (2, 2)
4. (1, 2) to (3, 2)
5. (2, 4) to (2, 2)
6. (3, 2) to (1, 2)

The game ends with two pegs and the rating Very Good.

## Files

- solitaire.py defines the board hierarchy and shared game rules.
- gui.py defines the Tkinter window and user interactions.
- tests/test_solitaire.py contains the two Sprint 2 tests.
- tests/test_manual_game.py adds eight Sprint 3 tests.
