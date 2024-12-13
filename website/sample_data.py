# from datetime import datetime
# from website import db
# from .models import Progress, Subtask, User, Task, Step, Tag
# from .models import user_task_association_table, user_tag_association_table

# def add_sample_data():
#     '''Add sample data to the database for testing purposes.'''
#     # Create or fetch users
#     users_data = [
#         "obraym25@colby.edu",
#         "ybmold25@colby.edu",
#         "pyang25@colby.edu",
#         "aerefe26@colby.edu"
#     ]

#     users_name = [
#         "Owen",
#         "Yela",
#         "Tricia",
#         "Atakan"
#     ]
#     # Add users if they don't already exist in the database
#     users = []
#     for email, name in zip(users_data, users_name):
#         existing_user = User.query.filter_by(email=email).first()
#         if not existing_user:
#             new_user = User(email=email, name=name)
#             db.session.add(new_user)
#             users.append(new_user)
#         else:
#             users.append(existing_user)
#     db.session.commit()

#     # Create a task (this task can be assigned to multiple users)
#     cur_task = Task.query.filter_by(title="First Year Check In").first()
#     if not cur_task:
#         cur_task = Task(title="First Year Check In", content="This is a sample task.")
#         db.session.add(cur_task)
#         db.session.commit()

#     # Check if the user-task association already exists before adding
#     # Set of user IDs already associated with this task
#     existing_users_in_task = set(user.id for user in cur_task.users)
#     users_to_add = [user for user in users if user.id not in existing_users_in_task]

#     if users_to_add:
#         # Add users who are not yet associated with the task
#         for user in users_to_add:
#             cur_task.users.append(user)
#         db.session.commit()

#     # repeat for task2
#     task2 = Task.query.filter_by(title="Get Social Security Number").first()
#     if not task2:
#         task2 = Task(title="Get Social Security Number", content="This is a second sample task.")
#         db.session.add(task2)
#         db.session.commit()

#     existing_users_in_task2 = set(user.id for user in task2.users)
#     # print("task2 existing users: ", existing_users_in_task2)
#     user_to_add_task2 = User.query.filter_by(name="Tricia").first()
#     # print("Tricia to add: ", user_to_add_task2)

#     if user_to_add_task2:
#         if user_to_add_task2.id not in existing_users_in_task2:
#             # Add users who are not yet associated with the task
#             task2.users.append(user_to_add_task2)
#         db.session.commit()


#     # Create subtasks and assign them to the task
#     subtasks_data = [
#         {"title": "I-20 Signature", "content":
#          "Go to Aura Moreno's office in Cotter Union 239 to get your I-20 signed."},
#         {"title": "Get US Phone Number", "content":
#          "Pick up a SIM card from the Pugh Center or use a free Google Voice number."},
#         {"title": "Bla Bla Bla 1", "content": "Bla Bla Bla 1"},
#         {"title": "Bla Bla Bla 2", "content": "Bla Bla Bla 2"},
#         {"title": "Bla Bla Bla 3", "content": "Bla Bla Bla 3"},
#     ]

#     steps_data = [
#         {"title": "Step 1", "content": "Bsdkfmksdf"},
#         {"title": "Step 2", "content": "sdv,sdlvsd"},
#         {"title": "Step 3", "content": "sdvkmsdmfmg"},
#         {"title": "Step 4", "content": "grekmtmrkey"},
#         {"title": "Step 5", "content": "sef,k,lrdkg"},
#     ]

#     subtasks = []
#     steps_list = []
#     for subtask_data in subtasks_data:
#         cur_subtask = Subtask.query.filter_by(title=subtask_data["title"],
#                                               task_id=cur_task.id).first()

#         if not cur_subtask:
#             cur_subtask = Subtask(title=subtask_data["title"], content=subtask_data["content"],
#                                   task_id=cur_task.id)
#             db.session.add(cur_subtask)
#             subtasks.append(cur_subtask)

#     for cur_subtask in subtasks:
#         for step_data in steps_data:
#             step = Step.query.filter_by(title=step_data["title"], subtask_id=cur_subtask.id).first()
#             if not step:
#                 step = Step(title=step_data["title"], content=step_data["content"],
#                             subtask_id=cur_subtask.id, progress=0)
#                 db.session.add(step)
#                 steps_list.append(step)

#     db.session.commit()

#     # Track progress for each user on the same task
#     progress_data = [
#         {"user": users[0], "subtasks_completed": [1, 2, 3]},  # User 1 has completed subtasks 1,2,3
#         {"user": users[1], "subtasks_completed": [2, 4]},     # User 2 has completed subtasks 2,4
#         {"user": users[2], "subtasks_completed": [3, 5]},     # User 3 has completed subtasks 3,5
#         {"user": users[3], "subtasks_completed": [1, 4, 5]}    # User 4 has completed subtasks 1,4,5
#     ]

#     # For each user, create progress records for their respective subtasks
#     for progress_entry in progress_data:
#         user = progress_entry["user"]
#         for i, cur_subtask in enumerate(subtasks):
#             cur_progress = Progress.query.filter_by(user_id=user.id,
#                                                     subtask_id=cur_subtask.id).first()
#             if not cur_progress:
#                 complete = i + 1 in progress_entry["subtasks_completed"]
#                 cur_progress = Progress(complete=complete, user_id=user.id,
#                                         subtask_id=cur_subtask.id, task_id=cur_task.id)
#                 db.session.add(cur_progress)
#     db.session.commit()

#     # tags list
#     tags_to_create = []

#     # Co'25 tag
#     co25_tag = Tag.query.filter_by(name="Co'25").first()
#     if not co25_tag:
#         co25_tag = Tag(name="Co'25", html_class="bg-warning")
#         tags_to_create.append(co25_tag)

#     # Co'26 tag
#     co26_tag = Tag.query.filter_by(name="Co'26").first()
#     if not co26_tag:
#         co26_tag = Tag(name="Co'26", html_class="bg-success")
#         tags_to_create.append(co26_tag)

#     # opt_tag
#     opt_tag = Tag.query.filter_by(name="OPT").first()
#     if not opt_tag:
#         opt_tag = Tag(name="OPT", html_class="bg-primary")
#         tags_to_create.append(opt_tag)

#     # cpt_tag
#     cpt_tag = Tag.query.filter_by(name="CPT").first()
#     if not cpt_tag:
#         cpt_tag = Tag(name="CPT", html_class="bg-danger")
#         tags_to_create.append(cpt_tag)

#     # committing tags
#     if tags_to_create:
#         db.session.add_all(tags_to_create)
#         db.session.commit()

#     tag_assignments = {
#         "Co'25": ["Yela", "Tricia", "Owen"],
#         "Co'26": ["Atakan"],
#         "CPT": ["Tricia", "Atakan"],
#         "OPT": ["Yela", "Owen"]
#     }

#     all_tags = {tag.name: tag for tag in Tag.query.all()}
#     all_users = {user.name: user for user in User.query.all()}

#     tags_to_update = {}

#     for tag_name, user_names in tag_assignments.items():
#         tag = all_tags.get(tag_name)
#         if tag:
#             existing_user_ids = {user.id for user in tag.users}
            
#             users_to_add = [
#                 all_users[user_name]
#                 for user_name in user_names
#                 if user_name in all_users and all_users[user_name].id not in existing_user_ids
#             ]
            
#             if users_to_add:
#                 tag.users.extend(users_to_add)
#                 tags_to_update[tag_name] = users_to_add

#     # committng all tag updates
#     if tags_to_update:
#         db.session.commit()

# def add_task_ssn_application():
#     '''Add a sample task for applying for a Social Security Number and Card.'''
#     # Add the main task
#     cur_task = Task.query.filter_by(title="Applying for a Social Security Number and Card").first()
#     if not cur_task:
#         cur_task = Task(
#             title="Applying for a Social Security Number and Card",
#             content="Steps and requirements for applying for an SSN.",
#             deadline=datetime(2020, 10, 20)  # Replace with the correct date format
#         )
#         db.session.add(cur_task)
#         db.session.commit()

#     # Assign the task to the hardcoded user "Owen"
#     user_owen = User.query.filter_by(name="Owen").first()
#     if user_owen and user_owen not in cur_task.users:
#         cur_task.users.append(user_owen)
#         db.session.commit()

#     # Define subtasks
#     subtasks_data = [
#         {
#             "title": "Requirements",
#             "content": "Understand the prerequisites and importance of a Social Security Number."
#         },
#         {
#             "title": "Applying for SSN",
#             "content": "Documents and steps to apply for an SSN."
#         },
#         {
#             "title": "Once You Receive SSN Card",
#             "content": "Steps to complete after receiving the SSN card."
#         },
#     ]

#     # Add subtasks
#     subtasks = []
#     for subtask_data in subtasks_data:
#         cur_subtask = Subtask.query.filter_by(title=subtask_data["title"], task_id=cur_task.id).first()
#         if not cur_subtask:
#             cur_subtask = Subtask(title=subtask_data["title"], content=subtask_data["content"],
#                                   task_id=cur_task.id)
#             db.session.add(cur_subtask)
#             subtasks.append(cur_subtask)
#     db.session.commit()

#     # Define steps for each subtask
#     # Sample data would be very bulky if in pytest format
#     # pylint: disable=all
#     steps_data = {
#         "Requirements": [
#             {"title": "Understanding the Importance of SSN", "content": """As an incoming international student to Colby, you will need to apply for a Social Security Number with the Social Security Administration Office regardless of whether you will be working on campus. 
#             The importance of this number is for Colby to pay you for your on-campus work and to report proper income and tax information to the Internal Revenue Service (IRS) on your behalf. Income can be in the form of two ways: scholarships (both Colby grant and awards) and compensation (from on-campus employment). If you are currently the recipient of a Colby grant, we are not able to post/release your Colby grant to your student account until your Social Security Number is received and entered into our system.
#             """},
#             {"title": "Prerequisites for Applying for an SSN", "content": """Prerequisites for Applying for an SSN
#             Your SEVIS record must be in Active status for at least 2 days before applying for a SSN.  You should also wait at least 10 days after your initial entry to the United States to ensure your information is uploaded into the system.  If you have a record in any other status, you will not be successful in applying for a SSN. 
#             Logistics to obtain a SSN and Social Security Card: 
#             •	We have arranged that you can reach out to Security for the Jitney at 207-859-5530. Please try to organize yourselves so that you go as a group of no more than 7, if you can. 
#             •	We would like to maximize this service. Let them know where you wish to go and the Jitney will transport you there and back. 
#             •	Please make sure you also check the office of hours between making these arrangements.
#             """},
#         ],
#         "Applying for SSN": [
#             {"title": "Required Documents for SSN Application", "content": """Bring the following documents:  
#             Complete and print Application for a Social Security Card form (SS-5).
#             Original passport
#             Form I-94 printed from https://i94.cbp.dhs.gov/I94/#/home
#             Original I-20 form (for F-1 visa holders only)
#             Original DS-2019 form (for J-1 visa holders only)
#             For F-1 or J-1 visa holders: Proof of employment or employment eligibility (see below for details)
#             """},
#             {"title": "Visiting the Social Security Office", "content": """Visit the Social Security Administration Office in Waterville at 14 Colby Street. Office hours Monday through Friday, 9am-4pm."""},
#             {"title": "Receiving Your Social Security Card", "content": """You will receive a Social Security card in the mail approximately one to two weeks after applying for it. If you have questions while waiting to receive your Social Security number, contact the Social Security Administration directly at 800.772.1213."""}
#         ],
#         "Once You Receive SSN Card": [
#             {"title": "Submitting Your SSN to Colby", "content": """F-1 and J-1 Visa Holders: Once you receive your Social Security number, you must use the following link to enter your SSN:https://www.colby.edu/humanresources/wp-content/uploads/sites/170/2022/10/Entering-Government-ID-From-Profile.pdf"""},
#             {"title": "Safeguarding Your SSN", "content": """This is a very private identification document and number and should be kept in a safe place where you won’t lose it. You should only need to provide it to employers, and possibly banks or other official institutions.  We recommend that you not carry it with you in your wallet or purse."""},
#             {"title": "Avoiding SSN-Related Scams", "content": """Beware of scam phone calls asking for your SSN or alerting you that yours has been canceled or you owe money or the like. There are many scams that target foreign nationals. If you receive any communications you are unsure about, please let Aura Moreno know and do not provide information to the caller.  In general, the Social Security Administration will never call you and then ask you to provide your Social Security Number over the phone."""}
#         ],
#     }
#     # pylint: enable=all

#     # Add steps
#     for cur_subtask in subtasks:
#         subtask_steps = steps_data.get(cur_subtask.title, [])
#         for step_data in subtask_steps:
#             step = Step.query.filter_by(title=step_data["title"], subtask_id=cur_subtask.id).first()
#             if not step:
#                 step = Step(
#                     title=step_data["title"],
#                     content=step_data["content"],
#                     subtask_id=cur_subtask.id,
#                     progress=0
#                 )
#                 db.session.add(step)
#     db.session.commit()

#     # Track progress for the user "Owen" on the new task
#     # Example: Owen has completed subtasks 1 and 2
#     progress_data = [{"user": user_owen, "subtasks_completed": [1, 2]}]

#     # For each user, create progress records for their respective subtasks
#     for progress_entry in progress_data:
#         user = progress_entry["user"]
#         for i, cur_subtask in enumerate(subtasks):
#             cur_progress = Progress.query.filter_by(user_id=user.id,
#                                                     subtask_id=cur_subtask.id).first()
#             if not cur_progress:
#                 complete = i + 1 in progress_entry["subtasks_completed"]
#                 cur_progress = Progress(complete=complete, user_id=user.id,
#                                         subtask_id=cur_subtask.id, task_id=cur_task.id)
#                 db.session.add(cur_progress)
#     db.session.commit()
