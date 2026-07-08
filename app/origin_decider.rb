# frozen_string_literal: true
# Origin: Decider '26 — DragonRuby GTK skeleton (PSEUDO-CODE / prototype)
# Theme: State of Origin 2026 Game 3, QLD Maroons vs NSW Blues @ Suncorp.
# Fan game — for entertainment, not a real prediction or official product.
#
# Entry point for DragonRuby is `tick(args)`. (Gosu users: map scenes onto
# Window#update/#draw and reuse the same Genesis/Simulator classes verbatim.)

# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------
COLORS = { maroon: [108, 29, 69], blue: [15, 82, 186], grass: [58, 139, 58],
           night: [16, 24, 40], light: [255, 246, 214] }.freeze

Player = Struct.new(:name, :impact, :role, :stamina, :origin)
Plan   = Struct.new(:aggression, :kick_focus) # 0.0..1.0 sliders

CAP = 120        # total impact allowed across the 17
HOME_MULT = 1.10 # Suncorp crowd edge for QLD

def pool_for(team)
  # In production, load from data/*.yml. Starters skew high, bench lower.
  # (name, impact, role, stamina, origin)
  # ...seeded from the 2026 Game 3 squads...
end

# ---------------------------------------------------------------------------
# GENESIS — build 13 starters + 4 bench under the cap and position rules
# ---------------------------------------------------------------------------
class Genesis
  MIN_ROLES = { hooker: 1, forward: 4, half: 2, back: 4 }.freeze

  def initialize(pool) = (@pool, @picked = pool, [])

  def toggle(player)
    @picked.include?(player) ? @picked.delete(player) : @picked << player
  end

  def total_impact = @picked.sum(&:impact)
  def picked?(player) = @picked.include?(player)
  def picked_count = @picked.size
  attr_reader :picked

  def valid?
    return false unless @picked.size == 17
    return false if total_impact > CAP
    MIN_ROLES.all? { |role, n| @picked.count { _1.role == role } >= n }
  end

  def build(team, plan)
    starters = @picked.first(13)
    bench    = @picked.last(4)
    { team: team, starters: starters, bench: bench, plan: plan }
  end
end

# ---------------------------------------------------------------------------
# SIMULATOR — advance the 80' decider; momentum + stamina + home edge
# ---------------------------------------------------------------------------
class Simulator
  attr_reader :clock, :score, :ticker

  def initialize(home, away, home_team, plan_h, plan_a)
    @sides = { home_team => [home, plan_h, true],
               opp(home_team) => [away, plan_a, false] }
    @score = Hash.new(0)
    @clock = 0            # match minutes 0..80
    @ticker = []          # rolling commentary lines
  end

  # Called each game-tick; ~1 match-minute per few frames.
  def step
    return if over?
    @clock += 1
    @sides.each do |team, (squad, plan, home)|
      strength = live_strength(squad, plan, home)
      @score[team] += 6 if try?(strength)      # converted try ≈ 6
      @score[team] += 2 if !try?(strength) && penalty?(strength)
    end
    log_moment
  end

  def live_strength(squad, plan, home)
    fade = 1.0 - (@clock / 80.0) * 0.3 * (1 - bench_stamina(squad)) # decay
    base = squad[:starters].sum(&:impact) * fade
    base *= (0.8 + plan.aggression * 0.4)   # aggression tilts scoring variance
    base *= HOME_MULT if home
    base * (0.5 + rand)                      # tonight's variance
  end

  def bench_stamina(squad)
    (squad[:bench].sum(&:stamina) / (squad[:bench].size * 10.0))
  end

  def try?(s)     = rand < (s / 4000.0)
  def penalty?(s) = rand < (s / 6000.0)
  def over?       = @clock >= 80 && @score.values.uniq.size > 1
  def opp(t)      = t == :QLD ? :NSW : :QLD

  def log_moment
    lead = @score.max_by { _2 }
    @ticker.unshift("#{@clock}'  #{@score[:QLD]}-#{@score[:NSW]}  #{lead[0]} edge")
    @ticker = @ticker.first(5)
  end

  def mvp(squads)
    squads.flat_map { _1[:starters] }.max_by { _1.impact * (0.5 + rand) }
  end
end

# ---------------------------------------------------------------------------
# WIN CONDITION — map final score to the series result (start state 1-1)
# ---------------------------------------------------------------------------
def resolve_series(state, sim)
  winner = sim.score.max_by { _2 }.first
  state.match.series[winner] += 1
  if state.match.series[state.side] == 2
    "SERIES WON 2-1 — #{state.side} lift the shield!"
  else
    "Series lost 1-2. Next year."
  end
end

# ---------------------------------------------------------------------------
# CORE LOOP — single tick, dispatches on the current scene
# ---------------------------------------------------------------------------
def tick(args)
  s = args.state
  s.scene ||= :menu
  send("scene_#{s.scene}", args)
end

def scene_menu(args)
  render_stadium(args)                       # night field + floodlights + crowd
  label(args, "ORIGIN: DECIDER '26", 640, 500)
  label(args, "Series 1-1 · Suncorp · pick your side", 640, 440)
  if button(args, "MAROONS") then start_genesis(args, :QLD) end
  if button(args, "BLUES", x: 780) then start_genesis(args, :NSW) end
  watermark(args, "Fan game — entertainment only")
end

def start_genesis(args, side)
  args.state.side    = side
  args.state.genesis = Genesis.new(pool_for(side))
  args.state.scene   = :genesis
end

def scene_genesis(args)
  g = args.state.genesis
  render_stadium(args)
  args.state.pool.each { |p| draw_player_chip(args, p, selected: g.picked?(p)) }
  label(args, "Impact #{g.total_impact}/#{CAP}   Picked #{g.picked_count}/17", 640, 60)
  handle_chip_clicks(args) { |p| g.toggle(p) }
  args.state.scene = :plan if g.valid? && button(args, "LOCK IN SQUAD")
end

def scene_plan(args)
  render_stadium(args)
  slider(args, :aggression); slider(args, :kick_focus)
  args.state.scene = :sim if button(args, "KICK OFF") && setup_sim(args)
end

def scene_sim(args)
  sim = args.state.sim
  3.times { sim.step }                       # a few match-minutes per frame
  render_stadium(args)
  draw_scoreboard(args, sim.score, sim.clock)
  draw_ticker(args, sim.ticker)
  args.state.scene = :result if sim.over?
end

def scene_result(args)
  render_stadium(args)
  msg = args.state.result ||= resolve_series(args.state, args.state.sim)
  label(args, msg, 640, 420)
  label(args, "MVP: #{args.state.sim.mvp(args.state.squads).name}", 640, 360)
  args.state.scene = :menu if button(args, "PLAY AGAIN")
  watermark(args, "Fan game — entertainment only")
end

# ---------------------------------------------------------------------------
# RENDER HELPERS (simplified Australian stadium)  — sketched signatures
# ---------------------------------------------------------------------------
def render_stadium(args)
  # 1. night backdrop  2. crowd arcs (maroon loud + blue pocket, shimmer)
  # 3. green field rect + white try/halfway lines  4. four floodlight glows
end
def draw_scoreboard(args, score, clock); end   # stadium-screen style QLD vs NSW
def draw_ticker(args, lines); end              # commentary crawl at the bottom
def draw_player_chip(args, player, selected:); end
# label/button/slider/watermark/handle_chip_clicks: thin DragonRuby primitives.

# Gosu note: this file is engine-agnostic below the render helpers — Genesis,
# Simulator, and resolve_series drop straight into a Gosu::Window unchanged.
