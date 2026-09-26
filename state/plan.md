# Execution plan

max_parallel = 8 (a platform limit, not a promise of simultaneity)

- batch 0: 00A, 00B, 01B, 11A, 11B, 11C, 16A, 16B
- batch 1: 02A, 02B, 17A, 17B, 17C, 17D, 17E, 18A
- batch 2: 18B, 18C, 18D, 18E, 19A, 19B, 19C, 19D
- batch 3: 19E, 20A, 20B, 20C, 20D, 20E, 21A, 21B
- batch 4: 21C, 21D, 21E, 22A, 22B, 22C, 22D, 23A
- batch 5: 23B, 23C, 23D, 23E, 24A, 24B, 24C, 24D
- batch 6: 24E, 25A, 25B, 25C, 25D, 26A, 26B, 26C
- batch 7: 26D, 26E
- batch 8: 03A, 03B, 03C, 04A, 04B, 05A, 05C, 09A
- batch 9: 09B, 09C, 10A, 10B, 10C, 25E
- batch 10: 01A, 04C, 07A, 07B, 07C, 08A, 08B, 08C
- batch 11: 13A, 13B, 13C, 14A, 22E
- batch 12: 05B, 12A, 12B, 12C, 14B, 16C, 27A, 27C
- batch 13: 27D
- batch 14: 06A, 06B, 06C, 27B
- batch 15: 01C, 14C, 27E
- batch 16: 02C, 28A, 28B, 28C, 28D, 28E
- batch 17: 15A, 15B, 15C
- batch 18: 00C
