from SnowAvalancheData.Statistics.Binning import Binning1D, Interval

binning = Binning1D(Interval(100, 1000), bin_width=100)
print(binning.number_of_bins)
print(binning.bin_width)
print(binning.interval)
print(binning.under_flow_bin)
print(binning.first_bin)
print(binning.last_bin)
print(binning.over_flow_bin)
print(binning.array_size)

for i in range(binning.array_size):
    print(binning.bin_interval(i))

for i in range(binning.array_size):
    print('low', i, binning.bin_lower_edge(i))
    print('upper', i, binning.bin_upper_edge(i))

print(binning.bins())
print(binning.bin_lower_edges())
print(binning.bin_centers())
