.. image:: image/getty_10.jpg
  :width: 400
  :alt: Getty the Goblin Picture 10
  
Overview:
---------

The PCFG Guesser is a tool meant to support password cracking attacks. At a high level, it reads in a previously trained PCFG grammar, and then outputs password guesses based on that grammar to stdout for use in an actual password cracking tool. Therefore as the name implies this tool only generates "guesses". It doesn't actually crack any passwords on its own.

The PCFG Guesser is currently aggressively single threaded. The only part where threading is currently used is to check for the user pressing a key so that it can print out the status/help messages. This focus on not parallelizing the guesser may seem odd considering that this tool is CPU bound and the slowness of it hurts the viability of using PCFGs in a password cracking session. I wish I had a deep technical reason that shows great insight to respond to this, but I don't. The reason why it's single threaded is every time I attempted to add parallization, it actually slowed the program down. If you can improve the performance and succeed where I failed, I'm all about that.

Generation of Pre-Terminals:
----------------------------

- One thing that on retrospect may cause a bit of confusion, is that the ``pqueue`` referenced in ``cracking_session.py`` is NOT a traditional Priority Queue, but is instead a ``PcfgQueue``. Now, the PcfgQueue does contain a priority queue itself, and operates by popping the most probable pre-terminal structure off of it. But it also contains the current "Next" algorithm implementation that converts the PCFG DAG into a Tree structure. To learn more about this please refer to the "PCFG Next Function Design" section of this Developer's Guide. Suffice to say, a lot of stuff is happening in the background when you call ``pqueue.pop()``.

- Now the next question you may be asking yourself is "What exactly is a pre-terminal". Technically that refers to a PCFG parse tree where all of the transitions have not been completed as terminals. When it comes to the PCFG Guesser though, this takes on a special meaning. In this context, it means that all of the remaining transitions lead to leaf nodes of the same probability. Therefore all terminals/guesses generated by this pre-terminal will have the exact same probability. This is really important since guesses can now be generated from them without having to do any more probability calculations. Think of these pre-terminals as very fine-grained wordlist rules in your more traditional password cracking programs, with the caveat that these pre-terminals not only define the traditional mangling rules to use, but also the "wordlist" to operate upon.

- Once a pre-terminal is defined, the PCFG guesser can then generate password guesses from it and then output those guesses to stdout. This looks much like you would find in a more traditional password cracker. This is also a horribly slow step thanks to Python's abysmal I/O latency and overhead. Seriously, every time I profile my code I'm horrified by how poor Python is at outputting guesses in a timely fashion. If I didn't love writing Python code, and if Python wasn't so easy to run, I would never recommend Python scripts to be used to generate the input for password crackers.

Future Areas of Research:
-------------------------

- Python is slow, C is much faster. You can find a C version of the PCFG guesser here: https://github.com/lakiw/compiled-pcfg

  - Note: My C coding skills leave a lot to be desired, and quite honestly I don't like coding in C. Therefore the compiled PCFG does not support all of the features of the Python version, and it is significantly more unstable.
  
  - That being said, it's wicked faster than the Python version!
  
  - Improving the C version of the guesser and potentially integrating it directly into other password cracking programs remains an item eternally on my to-do list. If you have any interest in doing this you have my full blessing.
  
- Currently the PCFG guesser outputs guesses in probability order. I'd really like to add support for generating guesses based on a probability limit instead. You can see more discussion about this in the "PCFG Next Function Design", but at a high level, being able to generate guesses via a limit would potentially allow parallelizing the guess generation process, and might even be something that could take advantage of GPU processing.

- Another neat feature would be to generate word mangling rules for other password cracking programs vs. generating guesses. This would remove all the performance issues with using PCFGs in a password cracking session. The biggest downside I can see is that the current PCFG does so well due to its ability to optimize the use of "words" in its wordlist. That would be difficult to translate over to more traditional password cracking rulesets. Aka the word "password" is really common so PCFG generated guesses contain it much more often than the word "zebra". It's hard to shoehorn that type of optimization into other password cracking rulesets though.