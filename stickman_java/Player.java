public class Player {
  String playerName;
  int playerType = 0;
  int wins = 0;
  int loss = 0;
  String[] winWords;
  String[] guessWords;
  String[] failWords;

  String opponentName;
  String[] opponentGuessedWords;

  Player(name, opponent, type);{
    playerName = name;
    opponentName = opponent;
    playerType = type;
  }

  public static void changePlayerType() {
    if (playerType == 1)
      playerType = 2;
    else playerType = 1;
  }

  public static void engGameStats() {
    if (player_type == 0)
      System.out.println("your had " + wins + " and " + losses +
      " losses\nYour guessed words were" + guessWords +
      " \nYou failed to guess " + failWords)
  }
}
