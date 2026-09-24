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
    // military & mental toughness
    'extreme-ownership': { title: 'Extreme Ownership', author: 'Jocko Willink & Leif Babin' },
    'discipline-freedom': { title: 'Discipline Equals Freedom', author: 'Jocko Willink' },
    'make-your-bed': { title: 'Make Your Bed', author: 'Adm. William H. McRaven' },
    'grit': { title: 'Grit', author: 'Angela Duckworth' },
    'obstacle-way': { title: 'The Obstacle Is the Way', author: 'Ryan Holiday' },
    'peak-performance': { title: 'Peak Performance', author: 'Brad Stulberg & Steve Magness' },
    // research (peer-reviewed studies)
    'study-dunedin': { title: 'Dunedin cohort study, PNAS 2011', author: 'Moffitt et al.' },
    'study-conscientiousness': { title: 'Terman Life Cycle Study, Ann. Behav. Med. 2009', author: 'Kern, Friedman et al.' },
    'study-grit': { title: 'Grit study incl. West Point cadets, JPSP 2007', author: 'Duckworth et al.' },
    'study-practice': { title: 'Deliberate practice meta-analysis, Psych. Science 2014', author: 'Macnamara, Hambrick & Oswald' },
    'study-if-then': { title: 'Implementation intentions meta-analysis, 2006', author: 'Gollwitzer & Sheeran' },
    'study-fitness': { title: 'Cardiorespiratory fitness & mortality, JAMA Netw Open 2018', author: 'Mandsager et al.' },
    'study-strength': { title: 'Resistance training & mortality meta-analysis, AJPM 2022', author: 'Shailendra et al.' },
    'study-steps': { title: 'Daily steps & mortality, Lancet Public Health 2022', author: 'Paluch et al.' },
    'study-social': { title: 'Social relationships & mortality, PLOS Medicine 2010', author: 'Holt-Lunstad, Smith & Layton' },
    'study-breath': { title: 'Structured breathing RCT, Cell Reports Medicine 2023', author: 'Balban et al.' },
    'study-seal': { title: 'Navy SEAL "Big Four" mental-toughness training', author: 'Eric Potterat (US Navy)' },
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
    // military & mental toughness
    ['extreme-ownership', ['character', 'bootcamp'], 'Own everything in your world. No blaming, no excuses. Leaders take responsibility for failures and give away the credit for wins.', 'Write down one thing that went wrong today and own it completely.'],
    ['extreme-ownership', ['goals', 'bootcamp'], 'Prioritise and execute: when everything is on fire, pick the single most important problem, solve it, then move to the next.', 'List today\'s problems and attack only the top one first.'],
    ['discipline-freedom', ['bootcamp', 'sleep'], 'Discipline creates freedom. The early alarm, the workout done, the money saved: each buys you options later.', 'Get up the moment the alarm sounds. No snooze.'],
    ['make-your-bed', ['bootcamp', 'habits'], 'Start the day with one task completed. A made bed is a small win that sets the tone, and a reminder that small things matter.', 'Make your bed within five minutes of waking.'],
    ['make-your-bed', ['character'], 'Life is not fair; move forward anyway. The standard doesn\'t lower because the conditions got worse.', 'Name one unfair thing today, then do your job anyway.'],
    ['grit', ['character', 'goals'], 'Talent counts, but effort counts twice: effort builds skill, and effort turns skill into achievement.', 'Put in one more focused rep on your most important skill.'],
    ['obstacle-way', ['character', 'mindset'], 'The obstacle in the path becomes the path. Treat setbacks as training material.', 'Reframe today\'s biggest obstacle as a drill you get to practise.'],
    ['peak-performance', ['pt', 'focus', 'sleep'], 'Stress + rest = growth. Push hard, then recover fully; growth happens in the rest.', 'Match every hard session with deliberate recovery tonight.'],
    ['cant-hurt-me', ['character', 'bootcamp'], 'Keep a "cookie jar" of hard things you have survived and reach into it when you want to quit.', 'Log today\'s hard thing so future-you can draw on it.'],
    // research-backed factors
    ['study-dunedin', ['character', 'bootcamp', 'finance'], 'In a 32-year study of 1,000 children, self-control predicted adult health, wealth and staying out of trouble, even between siblings. Self-control can also improve with age.', 'Pick one impulse to resist today and log it.'],
    ['study-conscientiousness', ['character', 'habits'], 'Conscientiousness (being organised, dependable and hard-working) is the personality trait most consistently linked to job performance, and it is also associated with living longer.', 'Finish one task you have been putting off, to completion.'],
    ['study-grit', ['character', 'goals'], 'Perseverance and passion for long-term goals predicted which West Point cadets made it through summer training better than their test scores did. The effect is real but modest.', 'Do one thing today for a goal that will take years.'],
    ['study-practice', ['learning', 'pt'], 'Deliberate practice matters most in games, music and sport, and less in education and professions. Practice is necessary but not the whole story, so train smart and pick the right arena.', 'Practise your weakest sub-skill with immediate feedback.'],
    ['study-if-then', ['goals', 'bootcamp', 'habits'], 'Across 94 studies, "if-then" plans (If X happens, then I will do Y) had a medium-to-large effect on actually reaching goals.', 'Write one if-then plan: "If it is 06:00, then I lace my shoes and run."'],
    ['study-fitness', ['pt', 'fitness'], 'In 122,000 adults, higher aerobic fitness meant lower mortality with no upper limit. The fittest group had about 80% lower risk than the least fit.', 'Do one session today that makes you breathe hard.'],
    ['study-strength', ['pt', 'fitness'], 'Any resistance training is linked to about 15% lower all-cause mortality; the benefit peaks around 30–60 minutes a week and adds up with aerobic training.', 'Get two 30-minute strength sessions into your week.'],
    ['study-steps', ['fitness', 'pt'], 'Across 15 cohorts, more daily steps meant lower mortality, levelling off around 8,000–10,000 steps for adults under 60.', 'Hit 8,000 steps before dinner.'],
    ['study-social', ['social'], 'Across 148 studies, people with stronger social relationships had about 50% higher odds of survival, an effect comparable to classic risk factors.', 'Schedule real time with someone who matters this week.'],
    ['study-breath', ['bootcamp', 'mindset'], 'Five minutes a day of exhale-focused breathing improved mood and lowered breathing rate more than the same time spent on mindfulness meditation.', 'Do five minutes of slow breathing with long exhales.'],
    ['study-seal', ['bootcamp', 'mindset'], 'The SEAL "Big Four" (micro-goals, mental rehearsal, command-style self-talk and breath control) were taught to help candidates handle fear and stress in selection.', 'Before your hardest task: set a micro-goal, picture it done, give yourself a command, then box-breathe.'],
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
