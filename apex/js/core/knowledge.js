/* Apex core: the Library. Principles from well-known books, summarised in our own words
 * (not quotations) and linked to the trackers they apply to. Used by the dashboard
 * ("principle of the day"), each tracker page, the #/library page, and the MCP server.
 * Works in the browser (window.Apex) and in Node (module.exports).
 */
(function (root) {
  const Apex = (root.Apex = root.Apex || {});

  const BOOKS = {
    'atomic-habits': { title: 'Atomic Habits', author: 'James Clear' },
    'tiny-habits': { title: 'Tiny Habits', author: 'BJ Fogg' },
    'deep-work': { title: 'Deep Work', author: 'Cal Newport' },
    'digital-minimalism': { title: 'Digital Minimalism', author: 'Cal Newport' },
    'stolen-focus': { title: 'Stolen Focus', author: 'Johann Hari' },
    'why-we-sleep': { title: 'Why We Sleep', author: 'Matthew Walker' },
    'outlive': { title: 'Outlive', author: 'Peter Attia' },
    'spark': { title: 'Spark', author: 'John J. Ratey' },
    'food-rules': { title: 'Food Rules', author: 'Michael Pollan' },
    'mindset': { title: 'Mindset', author: 'Carol S. Dweck' },
    'meditations': { title: 'Meditations', author: 'Marcus Aurelius' },
    'mans-search': { title: "Man's Search for Meaning", author: 'Viktor E. Frankl' },
    'peak': { title: 'Peak', author: 'Anders Ericsson & Robert Pool' },
    'make-it-stick': { title: 'Make It Stick', author: 'Brown, Roediger & McDaniel' },
    'essentialism': { title: 'Essentialism', author: 'Greg McKeown' },
    'the-one-thing': { title: 'The ONE Thing', author: 'Gary Keller & Jay Papasan' },
    '7-habits': { title: 'The 7 Habits of Highly Effective People', author: 'Stephen R. Covey' },
    'four-thousand-weeks': { title: 'Four Thousand Weeks', author: 'Oliver Burkeman' },
    'psychology-of-money': { title: 'The Psychology of Money', author: 'Morgan Housel' },
    'richest-man-babylon': { title: 'The Richest Man in Babylon', author: 'George S. Clason' },
    'your-money-your-life': { title: 'Your Money or Your Life', author: 'Vicki Robin & Joe Dominguez' },
    'win-friends': { title: 'How to Win Friends and Influence People', author: 'Dale Carnegie' },
    'good-life': { title: 'The Good Life', author: 'Robert Waldinger & Marc Schulz' },
    'cant-hurt-me': { title: "Can't Hurt Me", author: 'David Goggins' },
    'full-engagement': { title: 'The Power of Full Engagement', author: 'Jim Loehr & Tony Schwartz' },
  };

  // [book, modules, principle, action]
  const RAW = [
    // habits / systems
    ['atomic-habits', ['habits'], 'Small gains compound. Getting 1% better each day adds up to a huge difference over a year.', 'Pick one habit and make it slightly easier to do today.'],
    ['atomic-habits', ['habits', 'review'], 'Build habits around identity. Every time you act, you cast a vote for the kind of person you are becoming.', 'Write "I am the type of person who…" for your most important habit.'],
    ['atomic-habits', ['habits', 'digital'], 'Change your environment so good habits are obvious and bad ones are invisible.', 'Put one cue for a good habit where you will see it tomorrow morning.'],
    ['atomic-habits', ['habits'], 'Never miss twice. Missing one day is an accident. Missing two starts a new habit.', 'If you missed a habit yesterday, do the smallest version of it today.'],
    ['tiny-habits', ['habits'], 'Anchor new habits to existing routines: "After I [current habit], I will [new tiny habit]."', 'Attach a 30-second habit to something you already do every day.'],
    ['tiny-habits', ['habits', 'mindset'], 'Celebrating right after a behavior helps wire it in. Emotion creates habits.', 'Give yourself a small moment of celebration after each habit today.'],
    // focus / work
    ['deep-work', ['focus'], 'Hard, distraction-free concentration is becoming both rarer and more valuable.', 'Schedule one block of at least 90 minutes with your phone in another room.'],
    ['deep-work', ['focus', 'digital'], 'Every switch between tasks leaves "attention residue" that lowers the quality of the next task.', 'Batch email and messages into two or three set windows today.'],
    ['deep-work', ['focus', 'review'], 'End each workday with a shutdown ritual so your mind can actually rest.', 'Write tomorrow\'s first task before you stop working.'],
    ['stolen-focus', ['focus', 'digital'], 'Focus is not only willpower. Your environment and technology constantly compete for it.', 'Turn off every non-human notification on your phone.'],
    ['the-one-thing', ['goals', 'focus'], 'Ask: what\'s the ONE thing I can do such that, by doing it, everything else becomes easier or unnecessary?', 'Make that one thing your first priority today.'],
    ['essentialism', ['goals'], 'If you don\'t prioritize your life, someone else will. Fewer things, done better.', 'Cross one low-value commitment off your list this week.'],
    ['7-habits', ['goals', 'review'], 'Begin with the end in mind, and put first things first: important, not just urgent.', 'Spend 20 minutes today on something important but not urgent.'],
    ['four-thousand-weeks', ['goals', 'mindset'], 'Life is finite (about 4,000 weeks). You will never get everything done, so choose on purpose.', 'Decide what you will consciously neglect this week.'],
    ['full-engagement', ['focus', 'sleep'], 'Manage your energy, not just your time. Alternate intense effort with real recovery.', 'Take a genuine 10-minute break (no screens) after each focus block.'],
    // sleep
    ['why-we-sleep', ['sleep'], 'Consistent sleep and wake times anchor your body clock. Regularity matters as much as duration.', 'Set a fixed wake time and keep it on weekends too.'],
    ['why-we-sleep', ['sleep', 'learning'], 'Sleep consolidates memory. Learning without sleeping is like saving without backing up.', 'Protect sleep especially the night after you learn something important.'],
    ['why-we-sleep', ['sleep', 'nutrition'], 'Caffeine lingers for many hours, and alcohol fragments sleep even when it helps you fall asleep.', 'Have your last coffee before 2pm and skip alcohol tonight.'],
    ['why-we-sleep', ['sleep'], 'A cool, dark room and dimmed lights in the evening help your body start sleep.', 'Dim the lights and screens one hour before bed.'],
    // body
    ['outlive', ['fitness'], 'Exercise is one of the most powerful longevity tools you have. Build strength, stability, and cardio fitness.', 'Add one strength session and one zone-2 cardio session to your week.'],
    ['outlive', ['fitness', 'nutrition'], 'Muscle is protective as we age. Resistance training and enough protein preserve it.', 'Hit your protein target today and train one major muscle group.'],
    ['spark', ['fitness', 'mindset', 'learning'], 'Aerobic exercise boosts mood, focus, and the brain\'s capacity to learn.', 'Move for 20 minutes before your hardest thinking task.'],
    ['food-rules', ['nutrition'], 'Eat food, not too much, mostly plants. Choose things your great-grandparents would recognise.', 'Replace one processed item today with a whole-food alternative.'],
    ['food-rules', ['nutrition'], 'Stop eating when you\'re satisfied, not stuffed. Eat slowly and at a table.', 'Eat one meal today without a screen.'],
    ['cant-hurt-me', ['fitness', 'mindset'], 'When you think you\'re done, you usually still have more in reserve. Growth lives past the point of comfort.', 'Do one deliberately uncomfortable thing today and note how it felt.'],
    // mind
    ['mindset', ['mindset', 'learning'], 'Ability grows with effort. A growth mindset sees failure as information, not identity.', 'Add "yet" to one thing you can\'t do.'],
    ['meditations', ['mindset', 'review'], 'Focus on what is in your control (your judgments and actions) and let go of the rest.', 'Write down one worry and mark whether it is in your control.'],
    ['meditations', ['review'], 'Review each day honestly: what did I do well, where did I fall short, what is left undone?', 'Complete the evening review tonight.'],
    ['mans-search', ['mindset', 'goals'], 'Between stimulus and response there is a choice. Meaning can be found even in hardship.', 'Name what gives today meaning, even if it is small.'],
    ['full-engagement', ['mindset'], 'Positive emotions such as gratitude and appreciation are a renewable source of energy.', 'Write three specific things you\'re grateful for.'],
    // learning
    ['peak', ['learning', 'focus'], 'Expertise comes from deliberate practice: focused effort at the edge of your ability with fast feedback.', 'Practice the part of your skill you\'re worst at for 20 minutes.'],
    ['make-it-stick', ['learning'], 'Retrieval beats re-reading. Testing yourself and spacing out practice make learning last.', 'Close the book and write down what you remember from yesterday\'s reading.'],
    ['make-it-stick', ['learning'], 'Mixing (interleaving) related topics feels harder but produces deeper, more flexible learning.', 'Mix two related topics in today\'s study session.'],
    // digital
    ['digital-minimalism', ['digital'], 'Use technology on purpose. Keep only the tools that strongly support what you value.', 'Delete or log out of one app that doesn\'t earn its place.'],
    ['digital-minimalism', ['digital', 'mindset'], 'Solitude, time alone with your own thoughts and no inputs, is essential and disappearing.', 'Take a walk today without headphones or a phone.'],
    // money
    ['psychology-of-money', ['finance'], 'Doing well with money is more about behavior than intelligence. Patience and time drive compounding.', 'Automate one saving or investing transfer.'],
    ['psychology-of-money', ['finance'], 'Wealth is what you don\'t see: the money you didn\'t spend. Saving creates freedom and options.', 'Have a no-spend day, or skip one purchase you don\'t need.'],
    ['richest-man-babylon', ['finance'], 'Pay yourself first. Keep at least a tenth of all you earn before spending anything.', 'Move 10% of your next income straight into savings.'],
    ['your-money-your-life', ['finance'], 'Money is life energy. Measure each purchase by the hours of your life it cost.', 'Convert your biggest expense this week into hours worked.'],
    // relationships
    ['good-life', ['social'], 'In an 80-year Harvard study, the quality of relationships was the strongest predictor of health and happiness.', 'Reach out to someone you haven\'t talked to in a while.'],
    ['win-friends', ['social'], 'Be genuinely interested in other people. Remember names, listen more than you talk, and give honest appreciation.', 'Ask someone a question about their life and truly listen.'],
    ['7-habits', ['social'], 'Seek first to understand, then to be understood.', 'In your next disagreement, restate their view before giving yours.'],
  ];

  const principles = RAW.map(([book, modules, text, action], i) => ({
    id: i + 1, book, title: BOOKS[book].title, author: BOOKS[book].author, modules, text, action,
  }));

  // Stable per-day pick, so the "principle of the day" doesn't change on every render.
  function hash(s) {
    let x = 2166136261;
    for (let i = 0; i < s.length; i++) x = Math.imul(x ^ s.charCodeAt(i), 16777619);
    return Math.abs(x);
  }

  Apex.knowledge = {
    books: BOOKS,
    principles,
    forModule: (id) => principles.filter((p) => p.modules.includes(id)),
    /** One principle for a date, optionally restricted to some module ids. */
    daily(date, moduleIds) {
      const pool = moduleIds && moduleIds.length ? principles.filter((p) => p.modules.some((m) => moduleIds.includes(m))) : principles;
      const list = pool.length ? pool : principles;
      return list[hash(date + (moduleIds || []).join(',')) % list.length];
    },
    search(q) {
      q = String(q || '').toLowerCase();
      return principles.filter((p) => [p.text, p.action, p.title, p.author, p.modules.join(' ')].join(' ').toLowerCase().includes(q));
    },
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = Apex.knowledge;
})(typeof window !== 'undefined' ? window : globalThis);
