from crud_operations import MatchScheduler

class TournamentManager:
    def __init__(self):
        self.scheduler = MatchScheduler()
        
# Example Usage
if __name__ == "__main__":
    manager = TournamentManager()
    manager.main_menu()
