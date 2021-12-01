import pybgpstream
import pickle
import pandas as pd
from itertools import product
import warnings
from tqdm import tqdm
import multiprocessing as mp

def res_processing(chunks):
    list_result = []
    index=0
    for row in chunks:
        print(row)
        from_time = row[0]
        to_time = row[1]
        stream = pybgpstream.BGPStream(
            from_time=from_time, until_time=to_time,
            projects=["ris","routeviews"],
            record_type="updates",
            filter="prefix more 11.0.0.0/8"
        )
        stream.set_data_interface_option("broker", "cache-dir", "cache")
        j = 1
        for elem in stream:
            print(elem)
            list_result.append(elem)
#            with open('announcements_fromtime'+str(from_time)+ str(index) + '.txt', 'a+') as f:
#                f.write("%s\n" % elem)
        with open('data/announcements_per_address'+str(index)+'.pickle', 'wb') as handle:
            pickle.dump(list_result, handle, protocol=pickle.HIGHEST_PROTOCOL)
        index +=1

    print(list_result)

# Parallelizing using Pool.map()
if __name__ == "__main__":
    list = []
    dg = pd.read_csv('../data/timestamps_combined_squatting.csv', index_col=0)
    print(dg)
    # calculate the chunk size as an integer
    chunk_size = int(dg.shape[0] / 5)

    # this solution was reworked from the above link.
    # will work even if the length of the dataframe is not evenly divisible by num_processes
    chunks = [dg.loc[dg.index[i:i + chunk_size]] for i in range(0, dg.shape[0], chunk_size)]

    # pool = mp.Pool(5)
    #results = pool.map(res_processing, chunks)
    # chunks=[[1578848700,1578955500]]
    res_processing(chunks)