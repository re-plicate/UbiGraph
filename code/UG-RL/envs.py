from environment.uav_collection.env import *
from environment.uav_collection.log import *
from utils.base_utils import *
from main_setting import Params

params = Params()


class Make_Env(object):
    def __init__(self, device, num_steps, local_time, worker_id):
        '''
            num_steps: 最大时间步
        '''
        self.util = Util(device)
        self.time = str(local_time)
        self.env_gym = Env(Log(worker_id, num_steps, params.root_path, self.time))
        self.worker_id=worker_id
        self.num_steps = num_steps
        self.env_action = []
        self.env_cur_energy = []
        self.env_data_collection = []
        self.env_fairness = []
        self.env_efficiency = []
        self.env_energy_consumption = []
        self.env_age_of_information = []

        self.env_cur_energy.append([float(x) for x in list(self.env_gym.cur_uav_energy_list)])
        self.env_data_collection.append(self.env_gym.data_collection_ratio())
        self.env_fairness.append(self.env_gym.geographical_fairness())
        self.env_efficiency.append(self.env_gym.time_energy_efficiency())
        self.env_energy_consumption.append(self.env_gym.energy_consumption_ratio())
        self.env_age_of_information.append(self.env_gym.age_of_information())
        self.return_start = False
        self.target_poi_index = None
    def reset(self):
        self.step_counter = 0

        ob, uav_aoi_list, uav_snr_list, uav_tuse_list, uav_effort_list, cur_poi_data_val = self.env_gym.reset()  # [80,80,3]
        ob = ob.transpose(2, 0, 1)  # [3,80,80]

        ob = np.expand_dims(ob, axis=0)  # [1,3,80,80]
        uav_aoi_list = np.expand_dims(uav_aoi_list, axis=0)
        uav_snr_list = np.expand_dims(uav_snr_list, axis=0)
        uav_tuse_list = np.expand_dims(uav_tuse_list, axis=0)
        uav_effort_list = np.expand_dims(uav_effort_list, axis=0)
        self.return_start = False
        self.target_poi_index = None
        return torch.from_numpy(ob), torch.from_numpy(uav_aoi_list), torch.from_numpy(uav_snr_list), torch.from_numpy(
            uav_tuse_list), torch.from_numpy(uav_effort_list),torch.from_numpy(cur_poi_data_val)

    def render(self):
        self.env_gym.render()

    def get_uav_pos(self):
        return self.env_gym.get_uav_pos()


    def judge_finished(self, visited_pois, return_start):
        judgle = 0
        if return_start:
            # if len(visited_pois) == len(self.env_gym.poi_data_pos):
            for i in range(self.env_gym.uav_num):
                if self.env_gym.uav_state[i][-1] == 2:
                    judgle += 1
        if judgle == 2:
            visited_pois.append(tuple(self.env_gym.bs_pos[0]))
            return True
        else:
            return False

    def judgle_return(self, return_start, visited_pois):
        if return_start == False:
            if len(visited_pois) == len(self.env_gym.poi_data_pos)-self.env_gym.uav_num+1:
                # for poi_index, (poi_pos, poi_val) in enumerate(zip(self.env_gym.poi_data_pos, self.env_gym.cur_poi_data_val)):
                #     if poi_val!=0:
                #         self.target_poi_index = poi_pos
                self.env_gym.poi_data_pos = np.append(
                    self.env_gym.poi_data_pos,
                    self.env_gym.bs_pos,
                    axis=0
                )
                self.env_gym.init_poi_data_val = np.append(self.env_gym.init_poi_data_val, self.env_gym.uav_num)
                self.env_gym.cur_poi_data_val = np.append(self.env_gym.cur_poi_data_val, self.env_gym.uav_num)
                return True
            return False
        else:
            return True

    def step(self, action, current_step=None, current_episode=None, current_worker=None, visited_pois=None):

        self.step_counter += 1
        dead = False
        if self.step_counter <= self.num_steps:
            done = np.array([False])
        else:
            done = np.array([True])

        ob, r, d, uav_aoi_list, uav_snr_list, uav_tuse_list, uav_effort_list,cur_poi_data_val_list = self.env_gym.step(action=action,
                                                                                                 current_step=current_step,
                                                                                                 greedy_mode=params.use_opt,
                                                                                                 visited_pois=visited_pois,
                                                                                                 num_steps=self.num_steps
                                                                                                 )

        # TODO:!!!
        # if done == np.array([True]):
        #     for i in range(self.env_gym.uav_num):
        #        distance = self.env_gym.cal_distance(self.env_gym.cur_uav_pos[i], self.env_gym.bs_pos)
        #        if distance > 20:
        #            r += self.env_gym.sg.V["Return_PENALTY"]
        if done == np.array([True]):
            r += self.env_gym.sg.V["Return_PENALTY"]
        self.return_start = self.judgle_return(self.return_start, visited_pois)
        finished = self.judge_finished(visited_pois, self.return_start)
        for i in range(self.env_gym.uav_num):
            # skip the uav which runs out of energy
            if self.env_gym.dead_uav_list[i]:
                dead = True
        self.env_action.append([float(x) for x in list(np.reshape(action, [-1]))])
        self.env_cur_energy.append([float(x) for x in list(self.env_gym.cur_uav_energy_list)])
        self.env_data_collection.append(self.env_gym.data_collection_ratio())
        self.env_fairness.append(self.env_gym.geographical_fairness())
        self.env_efficiency.append(self.env_gym.time_energy_efficiency())
        self.env_energy_consumption.append(self.env_gym.energy_consumption_ratio())
        self.env_age_of_information.append(self.env_gym.age_of_information())

        ob = ob.transpose(2, 0, 1)  # [3,80,80]
        ob = np.expand_dims(ob, axis=0)  # [1,3,80,80]
        uav_aoi_list = np.expand_dims(uav_aoi_list, axis=0)
        uav_snr_list = np.expand_dims(uav_snr_list, axis=0)
        uav_tuse_list = np.expand_dims(uav_tuse_list, axis=0)
        uav_effort_list = np.expand_dims(uav_effort_list, axis=0)
        r = np.array([r], dtype=np.float32)  # [1]
        r = np.expand_dims(r, axis=0)  # [1,1]

        return torch.from_numpy(ob), torch.from_numpy(r), torch.from_numpy(done), torch.from_numpy(
            uav_aoi_list), torch.from_numpy(uav_snr_list), torch.from_numpy(
            uav_tuse_list), torch.from_numpy(uav_effort_list),torch.from_numpy(cur_poi_data_val_list),finished, dead

    def draw_path(self, step):
        self.env_gym.log.draw_path(self.env_gym, step)

    @property
    def log_path(self):
        return self.env_gym.log.full_path

    @property
    def observ_shape(self):
        return self.env_gym.observ.transpose(2, 0, 1).shape

    @property
    def action_space(self):
        return self.env_gym.uav_num * 3

    @property
    def num_of_uav(self):
        return self.env_gym.uav_num
