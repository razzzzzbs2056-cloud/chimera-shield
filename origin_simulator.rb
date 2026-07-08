# frozen_string_literal: true
# State of Origin Game Simulator — FAN SIMULATION ONLY (not a real prediction)

nsw = {
  starters: %w[Tedesco Bostock Best Crichton Nawaqanitawase Moses Cleary Haas Robson Barnett Young Marin Yeo],
  bench: %w[Murray Fonua-Blake Olakauatu Brailey Strange Koula Radley]
}
qld = {
  starters: %w[Ponga Cobbo Toia Tabuai-Fidow Fifita Munster Walker Flegler Grant Faasuamaleaui Nikora Capewell Cotter],
  bench: %w[Plath Carrigan Nanai Loiero Walsh Tualagi Horsburgh]
}
match = { venue: "Suncorp Stadium", home: :QLD, series: { QLD: 1, NSW: 1 }, decider: true }

SIMS = 10_000
HOME_BONUS = 1.10 # ~10% home-crowd lift

# Fixed per-player base impact 1-10 (starters skew higher than bench).
def rate(team)
  ratings = {}
  team[:starters].each { |p| ratings[p] = rand(6..10) } # 6-10
  team[:bench].each    { |p| ratings[p] = rand(2..7) }  # 2-7 (weighted lower)
  ratings
end

nsw_ratings = rate(nsw)
qld_ratings = rate(qld)

def score(ratings, home)
  total = ratings.sum { |_, r| r * (0.5 + rand) } # each player fires 0.5x-1.5x tonight
  total *= HOME_BONUS if home
  (total / 10.0).round # convert to a plausible footy score
end

wins = { NSW: 0, QLD: 0, draw: 0 }
totals = { NSW: 0, QLD: 0 }
mvp = Hash.new(0)
home = match[:home]

SIMS.times do
  n = score(nsw_ratings, home == :NSW)
  q = score(qld_ratings, home == :QLD)
  totals[:NSW] += n; totals[:QLD] += q
  if    n > q then wins[:NSW] += 1
  elsif q > n then wins[:QLD] += 1
  else  wins[:draw] += 1 end
  best = (nsw_ratings.merge(qld_ratings)).max_by { |_, r| r * (0.5 + rand) }.first
  mvp[best] += 1
end

winner = wins.max_by { |_, v| v }.first
top_player, top_count = mvp.max_by { |_, v| v }

puts "=== STATE OF ORIGIN #{match[:decider] ? 'DECIDER' : ''} — #{match[:venue]} ==="
puts "Series: QLD #{match[:series][:QLD]} - #{match[:series][:NSW]} NSW | Home: #{home}"
puts "Simulations run: #{SIMS}\n\n"
puts "Win probability:"
puts "  NSW  #{(wins[:NSW] * 100.0 / SIMS).round(1)}%  (#{wins[:NSW]})"
puts "  QLD  #{(wins[:QLD] * 100.0 / SIMS).round(1)}%  (#{wins[:QLD]})"
puts "  Draw #{(wins[:draw] * 100.0 / SIMS).round(1)}%"
puts "\nAverage score:  NSW #{(totals[:NSW].to_f / SIMS).round(1)} - #{(totals[:QLD].to_f / SIMS).round(1)} QLD"
puts "Probable winner: #{winner}"
puts "Top player (most MVP nights): #{top_player} (#{top_count})"
puts "\n** Fan simulation only — for entertainment, not a real prediction. **"
