import subprocess
import re
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Check model-wise migration errors and suggest solutions'

    def handle(self, *args, **kwargs):
        self.check_model_wise_migration_errors()

    def check_model_wise_migration_errors(self):
        """
        This function checks for migration errors in Django and provides potential solutions.
        It runs `python manage.py makemigrations` and `python manage.py migrate` commands
        and captures common migration errors.
        """
        
        # Step 1: Check for pending migrations (makemigrations)
        try:
            self.stdout.write("Checking for pending migrations...")
            makemigrations_output = subprocess.check_output(
                ['python', 'manage.py', 'makemigrations'], stderr=subprocess.STDOUT
            )
            self.stdout.write(makemigrations_output.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            makemigrations_error = e.output.decode('utf-8')
            self.stdout.write(self.style.ERROR("Error during makemigrations:"))
            self.stdout.write(self.style.ERROR(makemigrations_error))
            self.suggest_solution(makemigrations_error)
            return
        
        # Step 2: Attempt to run migrations (migrate)
        try:
            self.stdout.write("Applying migrations...")
            migrate_output = subprocess.check_output(
                ['python', 'manage.py', 'migrate'], stderr=subprocess.STDOUT
            )
            self.stdout.write(migrate_output.decode('utf-8'))
        except subprocess.CalledProcessError as e:
            migrate_error = e.output.decode('utf-8')
            self.stdout.write(self.style.ERROR("Error during migrations:"))
            self.stdout.write(self.style.ERROR(migrate_error))
            self.suggest_solution(migrate_error)
            return
        
        self.stdout.write(self.style.SUCCESS("Migrations applied successfully!"))

    def suggest_solution(self, error_message):
        """
        This function suggests possible solutions based on the error message.
        """
        # Common migration errors and solutions
        solutions = {
            'Table already exists': 'Solution: Try deleting the migration file or faking the migration with `--fake`.',
            'No such table': 'Solution: Ensure all previous migrations were applied, or try running `python manage.py migrate --fake-initial`.',
            'FieldError': 'Solution: Check if you added a new field without a default value. Add `null=True`, `blank=True`, or provide a `default`.',
            'ProgrammingError': 'Solution: This may be a database constraint error. Ensure foreign key relations and constraints are correctly defined.',
            'ValueError: Related model': 'Solution: Ensure that any ForeignKey or ManyToManyField references a valid and existing model.',
            'IntegrityError': 'Solution: This usually happens due to conflicts with existing data. Check for unique constraints or not null constraints.',
            'duplicate key value violates unique constraint': 'Solution: Remove duplicate entries in your database, or adjust the unique constraint in the model.',
            'cannot ALTER TABLE': 'Solution: If you are changing a field type, make sure to run a migration without data loss, or handle manual database changes.',
            'You are trying to add a non-nullable field': 'Solution: Either provide a default value or use `null=True` in your new field.',
        }
        
        # Check the error message for known issues
        for error, solution in solutions.items():
            if re.search(error, error_message, re.IGNORECASE):
                self.stdout.write(self.style.WARNING(f"Detected Error: {error}"))
                self.stdout.write(self.style.SUCCESS(f"Suggested Solution: {solution}"))
                return

        # If no known error pattern is matched
        self.stdout.write(self.style.ERROR("Error not recognized. Please check the full error trace and debug accordingly."))

