from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path
import uuid
import src.config as Config

class CostTracker:
    """
    Cost tracker using a simple list of cost records in a JSON file.
    Implements budget tracking and cost management for content generation services.
    """

    def __init__(self):
        # Base data directory for cost records - stores all cost-related data
        self.data_dir = Path("data/costs")

        # Central costs file path - single JSON file storing all cost records
        self.costs_file = self.data_dir / "costs.json"

        # Create directory if it doesn't exist - ensures data storage is available
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the costs file if it doesn't exist - creates empty cost record list
        if not self.costs_file.exists():
            self._initialize_costs_file()

    def _initialize_costs_file(self):
        """
        Create initial empty costs file.
        Sets up an empty list structure in JSON format for storing cost records.
        """
        with open(self.costs_file, 'w') as f:
            json.dump([], f)

    def track_cost(self, content_type: str, cost: float, prompt: str) -> str:
        """
        Track a new cost and save to the JSON file.

        Args:
            content_type (str): Type of content generated (image/song/research)
            cost (float): Cost of the generation operation
            prompt (str): User prompt that triggered the generation

        Returns:
            str: Unique identifier for the cost record

        Raises:
            ValueError: If adding the cost would exceed the configured budget
        """
        # Read existing costs from file
        with open(self.costs_file, 'r') as f:
            costs = json.load(f)

        # Calculate total existing costs to check against budget
        total_existing_cost = sum(record['cost'] for record in costs)

        # Check if new cost would exceed budget limit
        new_total = total_existing_cost + cost
        if new_total > Config.BUDGET:
            raise ValueError(f"Cost {cost} would exceed budget of {Config.BUDGET}")

        # Generate unique identifier for the record using UUID4
        record_id = str(uuid.uuid4())

        # Create detailed cost record with metadata
        record = {
            "id": record_id,
            "timestamp": datetime.now().isoformat(),
            "type": content_type,
            "cost": cost,
            "prompt": prompt
        }

        # Add record to list and save back to file
        costs.append(record)

        with open(self.costs_file, 'w') as f:
            json.dump(costs, f, indent=2)

        return record_id

    def get_costs(self) -> Dict:
        """
        Retrieve cost information from the file.

        Returns:
            Dict containing:
            - total_cost: Sum of all costs
            - remaining_budget: Available budget
            - costs_by_type: Costs grouped by content type
            - record_count: Total number of records
            - recent_costs: Last 10 cost records

        Note: Returns default values if file read fails
        """
        try:
            with open(self.costs_file, 'r') as f:
                costs = json.load(f)

            # Calculate total costs across all records
            total_cost = sum(record['cost'] for record in costs)

            # Group costs by content type for analysis
            costs_by_type = {}
            for record in costs:
                content_type = record['type']
                costs_by_type[content_type] = costs_by_type.get(content_type, 0) + record['cost']

            return {
                "total_cost": total_cost,
                "remaining_budget": Config.BUDGET - total_cost,
                "costs_by_type": costs_by_type,
                "record_count": len(costs),
                "recent_costs": costs[-10:]  # Last 10 records for quick reference
            }
        except Exception:
            # Return safe default values if file access fails
            return {
                "total_cost": 0.0,
                "remaining_budget": Config.BUDGET,
                "costs_by_type": {},
                "record_count": 0,
                "recent_costs": []
            }

    def get_record_by_id(self, record_id: str) -> Dict:
        """
        Retrieve a specific cost record by its ID.

        Args:
            record_id (str): UUID of the cost record to retrieve

        Returns:
            Dict: The complete cost record

        Raises:
            FileNotFoundError: If no record matches the provided ID
        """
        with open(self.costs_file, 'r') as f:
            costs = json.load(f)

        # Search for record with matching ID
        for record in costs:
            if record['id'] == record_id:
                return record

        raise FileNotFoundError(f"No record found with ID {record_id}")

    def delete_record(self, record_id: str) -> bool:
        """
        Delete a specific cost record.

        Args:
            record_id (str): UUID of the cost record to delete

        Returns:
            bool: True if record was found and deleted, False otherwise
        """
        # Read existing costs from file
        with open(self.costs_file, 'r') as f:
            costs = json.load(f)

        # Remove the record if found
        original_length = len(costs)
        costs = [record for record in costs if record['id'] != record_id]

        # Save only if a record was actually removed
        if len(costs) < original_length:
            with open(self.costs_file, 'w') as f:
                json.dump(costs, f, indent=2)
            return True

        return False