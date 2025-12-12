#!/bin/bash
# Re-enable the daily engineering summary email

echo "Re-enabling daily engineering summary email..."

# Remove the comment from the cron job
crontab -l | sed 's/^#0 16 \* \* 1-5.*daily_engineering_summary.py.*/0 16 * * 1-5 \/home\/mavrick\/Projects\/Secondbrain\/venv\/bin\/python \/home\/mavrick\/Projects\/Secondbrain\/daily_engineering_summary.py >> \/home\/mavrick\/Projects\/Secondbrain\/logs\/daily_summary.log 2>\&1/' | crontab -

echo "✅ Daily engineering summary email has been RE-ENABLED"
echo ""
echo "The email will now send at 4 PM Monday-Friday"
echo ""
crontab -l | grep "daily_engineering_summary"
