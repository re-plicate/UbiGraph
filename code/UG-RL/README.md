# UG-RL
## Installation
Install dependent packages
```sh
pip install -r requirements.txt
```


##  Training

Train our solution
```bash
# set "trainable=True" in main_setting.py
python main.py
```


## Testing

Test with the trained models 

```sh
# set "trainable=False" and "test_path" in main_setting.py
python main.py
```

Random test the env

```sh
python test_random_agent.py
```

## Reference
- https://github.com/ikostrikov/pytorch-a2c-ppo-acktr-gail



