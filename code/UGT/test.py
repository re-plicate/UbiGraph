import argparse
import json

if __name__ == "__main__":
    resultingJsonArray = []
    with open('workspace/parking-estimator/jsons/estimations_cwout.json', 'w+') as outfile:
        json.dump(resultingJsonArray, outfile)