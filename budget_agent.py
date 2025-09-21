from collections import defaultdict
from typing import List, Dict, Any

from base_agent import BaseAgent
# from backend.models import Trip, Expense

class BudgetAgent(BaseAgent):
    """
    An agent that handles live budget tracking and expense splitting for groups.
    This agent is more focused on business logic and calculations than generative AI.
    """

    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a specific budget-related task.

        Args:
            task: The task to perform ("calculate_per_diem", "get_split_summary").
            **kwargs: Arguments specific to the task.

        Returns:
            A dictionary containing the results of the task.
        """
        if task == "calculate_per_diem":
            return self._calculate_per_diem(**kwargs)
        elif task == "get_split_summary":
            return self._get_split_summary(**kwargs)
        else:
            return {"error": f"Unknown task: {task}"}

    def _calculate_per_diem(
        self,
        total_budget: float,
        pre_booked_costs: List[Dict],
        duration_days: int
    ) -> Dict[str, Any]:
        """
        Calculates the remaining budget and per diem spending money.

        Args:
            total_budget: The total budget for the trip.
            pre_booked_costs: A list of pre-booked expenses, e.g., [{'name': 'Flight', 'amount': 20000}, ...].
            duration_days: The total duration of the trip in days.

        Returns:
            A dictionary with the budget breakdown.
        """
        if duration_days <= 0:
            return {"error": "Trip duration must be greater than zero."}

        spent_on_bookings = sum(item.get('amount', 0) for item in pre_booked_costs)
        remaining_budget = total_budget - spent_on_bookings
        per_diem = remaining_budget / duration_days if remaining_budget > 0 else 0

        return {
            "total_budget": total_budget,
            "spent_on_bookings": spent_on_bookings,
            "remaining_for_trip": remaining_budget,
            "per_diem_estimate": round(per_diem, 2)
        }

    def _get_split_summary(self, expenses: List[Dict]) -> Dict[str, Any]:
        """
        Calculates who owes whom based on a list of expenses.

        Args:
            expenses: A list of expense dictionaries. Each dict should contain:
                      - 'amount': The total amount of the expense.
                      - 'payer_id': The ID of the user who paid.
                      - 'participants': A list of user IDs who were part of the expense.

        Returns:
            A dictionary with user balances and a list of transactions to settle debts.
        """
        balances = defaultdict(float)

        if not expenses:
            return {"balances": {}, "transactions_to_settle": [], "message": "No expenses logged."}

        for expense in expenses:
            amount = expense.get('amount', 0)
            payer_id = expense.get('payer_id')
            participants = expense.get('participants', [])

            if not all([amount > 0, payer_id, participants]):
                continue  # Skip invalid expense entries

            # The person who paid gets credited the full amount
            balances[payer_id] += amount

            # Each participant owes their share
            share = amount / len(participants)
            for participant_id in participants:
                balances[participant_id] -= share

        # Now, simplify the debts
        debtors = sorted([(user_id, balance) for user_id, balance in balances.items() if balance < 0], key=lambda x: x[1])
        creditors = sorted([(user_id, balance) for user_id, balance in balances.items() if balance > 0], key=lambda x: x[1], reverse=True)

        transactions = []
        debtor_idx, creditor_idx = 0, 0

        while debtor_idx < len(debtors) and creditor_idx < len(creditors):
            debtor_id, debt = debtors[debtor_idx]
            creditor_id, credit = creditors[creditor_idx]

            amount_to_transfer = min(abs(debt), credit)
            transactions.append({"from": debtor_id, "to": creditor_id, "amount": round(amount_to_transfer, 2)})

            debtors[debtor_idx] = (debtor_id, debt + amount_to_transfer)
            creditors[creditor_idx] = (creditor_id, credit - amount_to_transfer)

            if abs(debtors[debtor_idx][1]) < 0.01: debtor_idx += 1
            if creditors[creditor_idx][1] < 0.01: creditor_idx += 1
        
        final_balances = {user_id: round(balance, 2) for user_id, balance in balances.items()}

        return {
            "balances": final_balances,
            "transactions_to_settle": transactions
        }