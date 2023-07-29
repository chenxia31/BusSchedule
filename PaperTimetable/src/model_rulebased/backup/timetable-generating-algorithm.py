class Trip:
    def __init__():
        self.dt
        self.at
        self.direction
        # self.layover_time


class TripPair:
    def __init__():
        self.inbound_trip = Trip()
        self.outbound_trip = Trip()


class Headway:
    def __init__():
        self.values = {
            "6:00-7:00": [30],
            "7:00-8:00": [25, 20, 15]
            }

    def adjust():
        self.values = {
             "6:00-7:00": [30+5],
             "7:00-8:00": [25+5, 20+5, 15+5]
        }


class runningTime:
    def __init__():
        self.values = {
            "6:00-7:00": 50,
            "7:00-8:00": 60,
            }


class TripPairGroup:
    def __init__():
        self.block_dict = {
            first_block_trip: TripPair()
            first_block_trip: TripPair()
            first_block_trip: TripPair()
            first_block_trip: TripPair()
        }
    
    def insert(index=-1):
        modify self.block_dict
        return the last TripPair of the self.block_dict



class Timetable:
    def __init__():
        self.group_list = [
            # TripPairGroup, TripPairGroup, TripPairGroup
            ]

    def init_trip_pair_group(Headway, first_departure_moment):
        # try multiple times 30, 40, 50, 60
        Headway
        return InitTripPairGroup

    def search():
        headwayTripPairGroup, runningTimeTripPairGroup = self.generate_group(
            currentTripPairGroup.bottomTripPair)
        mark, group = self.generate_feasible_trip_pair_group(headwayTripPairGroup, runningTimeTripPairGroup)
        if mark:
            # not valid
            return False
        self.group_list.append(group)

    def generate_feasible_trip_pair_group(headwayTripPairGroup, runningTimeTripPairGroup):
        mark, tripPairGroup = self.operate_top_trip(headwayTripPairGroup, runningTimeTripPairGroup)

        
    def operate_top_trip(headwayTripPairGroup, runningTimeTripPairGroup):
        if satisfy_layover_time_rule:
            return True, headwayTripPairGroup
        else:
            layover_time_diff = self.cal_layovertime(topTrip) - self.cal_layovertime(currentTripPairGroup.topTrip)
            # positive or negative
            modified_tripPair = enumerate # 5, 10, ..., 5 * (n_block-1); O(n_block)
            if enume_invalid:
                valid, modified_tripPair = insert_virtual_trip_pair # max 2 times
                if not valid:
                    assert False, "enuma and redo init_trip_pair_group" # worst case
                else:
                    modified_group = self.generate_group(modified_tripPair, 
                    headway_list,
                    inbound_running_time_list, 
                    outbound_running_time_list, 
                    portion)
                    return True, modified_group
            else:
                modified_group = self.generate_group(modified_tripPair, 
                    headway_list,
                    inbound_running_time_list, 
                    outbound_running_time_list, 
                    portion)
                    return True, modified_group

    def generate_group(self, **kwargs):
        headwayTripPairGroup = # todo
        for tripPair in headwayTripPairGroup:
            if tripPair.departure_interval not in given_headway:
                if tripPair.layover_time cannot reduce:
                    continue
        if all tripPair.layover_time cannot reduce:
            raise NotImpelement("peek hour")

    def insert_virtual_trip_pair(currentTripPairGroup, block_work_mode):
        # todo: work duration
        # todo: the first trip of the block and the last trip of the block can be assigned as a virtual trip.
        if block_work_mode is "two class":
            # todo
            i = find_inserted_block()
            tripPair = currentTripPairGroup.insert(i)
        else
            tripPair = currentTripPairGroup.insert(-1)
        layover_time_diff = self.cal_layovertime(tripPair) - self.cal_layovertime(currentTripPairGroup.topTrip)
        # positive or negative
        enumerate 5, 10, ..., 5 * (n_block-1)
        if invalid:
            # todo
            assert False, "enuma and redo init_trip_pair_group" # worst case
        else:
            True, modified_tripPair
    
    def feasible(self, tripPairGroup1):
        layover_time_rule
        departure_interval_rule
        meal_time_rule
        work_time_rule

    def _cal_layovertime(self, tripPair):
        return layover_time


def main():
    headway = Headway()
    timetable = Timetable()
    timetable.init_trip_pair_group()
    mark, result = timetable.search()
    while mark:
        headway.adjust()
        mark, result = timetable.search()
        if condition:
            break
