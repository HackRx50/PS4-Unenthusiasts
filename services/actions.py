class ActionService:
    def __init__(self):
        self.actions = []

    def add_action(self, action_data: dict):
        self.actions.append(action_data)

    def get_all_actions(self):
        return self.actions

    def get_action_by_id(self, action_id: int):
        return next((action for action in self.actions if action['id'] == action_id), None)

    def delete_action(self, action_id: int):
        self.actions = [action for action in self.actions if action['id'] != action_id]
