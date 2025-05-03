import json
import asyncio
from datetime import timedelta
from django.utils.timezone import now as time
from django.urls import reverse
from django.db import transaction
from django.db.models import Q

from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from celery import shared_task

from apps.enquiries.models import (
    Enquiries, 
    EnquiryUser, 
    EstimationNotes, 
    Estimations, 
    Temp_EstimationNotes, 
    Temp_Estimations,
)
from apps.estimations.models import (
    Estimation_UserTimes, 
    Quotations, 
    Temp_Estimation_UserTimes, 
    Temp_Quotations,
)
from apps.helper import sum_times
from apps.user.models import User


# @shared_task
class EnquiryUserActivetime(AsyncWebsocketConsumer):
    async def connect(self):
        self.enquiry_id = self.scope['url_route']['kwargs']['enquiry_id']
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        # self.estimation_id = self.scope['url_route']['kwargs']['estimation_id']
        self.enquiry_group_name = f'enquiry_user_{self.enquiry_id}_{self.user_id}'
        # self.enquiry_group_name = f'enquiry_user_{self.enquiry_id}_{self.estimation_id}_{self.user_id}'
        await (self.channel_layer.group_add)(
            self.enquiry_group_name,
            self.channel_name
        )

        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.enquiry_group_name,
            self.channel_name
        )
        raise StopConsumer()
        
    async def receive(self, text_data):
        try:
            data_json = json.loads(text_data)
            timer = await self.update_timer(data_json)
            await self.channel_layer.group_send(
                self.enquiry_group_name,
                {
                    'type': 'send_data',
                    'data': json.dumps(timer),
                }
            )
        except json.JSONDecodeError:
            print("Invalid JSON format:", text_data)
        
    @database_sync_to_async
    def update_timer(self, data_json):
        time_data = data_json.get('time')
        status = data_json.get('status')
        estimation_id = data_json.get('estimation_id')
        temp = data_json.get('temp')
        
        hours, minutes, seconds = map(int, time_data.split(':'))
        timedelta_duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        
        if time_data:
            user_obj = User.objects.get(pk=self.user_id)
            enquiry_obj = Enquiries.objects.get(pk=self.enquiry_id)
            
            enquiry_user, estimation_user = self.get_enquiry_and_estimation_users(enquiry_obj, user_obj, status, temp, estimation_id)
            
            if not enquiry_user:
                enquiry_user = self.create_enquiry_user(user_obj, enquiry_obj, timedelta_duration, status)
            
            if not estimation_user:
                estimation_user = self.create_estimation_user(user_obj, estimation_id, timedelta_duration, status, temp)
            
            self.update_user_data(enquiry_user, estimation_user, timedelta_duration)
            self.save_users(enquiry_user, estimation_user)
            
            return {
                'active_time': str(enquiry_user.active_time),
                'last_update': str(enquiry_user.last_update),
            }

    def get_enquiry_and_estimation_users(self, enquiry_obj, user_obj, status, temp, estimation_id):
        if status:
            try:
                enquiry_user = EnquiryUser.objects.get(
                    enquiry=enquiry_obj, 
                    user=user_obj, 
                    date=time().date(), 
                    status=status,
                )
                
                if temp == 1:
                    try:
                        estimation_user = Temp_Estimation_UserTimes.objects.get(
                            estimation=estimation_id, 
                            user=user_obj, 
                            date=time().date(), 
                            status=status,
                        )
                    except Temp_Estimation_UserTimes.DoesNotExist:
                        estimation_user = None
                else:
                    try:
                        estimation_user = Estimation_UserTimes.objects.get(
                            estimation=estimation_id, 
                            user=user_obj, 
                            date=time().date(), 
                            status=status,
                        )
                    except Estimation_UserTimes.DoesNotExist:
                        estimation_user = None
                    
            except EnquiryUser.DoesNotExist:
                enquiry_user = None
                estimation_user = None
        else:
            enquiry_user = None
            estimation_user = None
            
        return enquiry_user, estimation_user

    def create_enquiry_user(self, user_obj, enquiry_obj, timedelta_duration, status):
        return EnquiryUser(
            user=user_obj, 
            enquiry=enquiry_obj, 
            active_time=timedelta_duration, 
            updated_at=time(), 
            date=time().date(), 
            status=status,
        )

    def create_estimation_user(self, user_obj, estimation_id, timedelta_duration, status, temp):
        if temp == 1:
            try:
                estimation_obj = Temp_Estimations.objects.get(pk=estimation_id)
                return Temp_Estimation_UserTimes(
                    user=user_obj, 
                    estimation=estimation_obj, 
                    active_time=timedelta_duration, 
                    updated_at=time(), 
                    date=time().date(), 
                    status=status,
                )
            except Exception:
                pass
        else:
            try:
                estimation_obj = Estimations.objects.get(pk=estimation_id)
                return Estimation_UserTimes(
                    user=user_obj, 
                    estimation=estimation_obj, 
                    active_time=timedelta_duration, 
                    updated_at=time(), 
                    date=time().date(), 
                    status=status,
                )
            except Exception:
                pass

    def update_user_data(self, enquiry_user, estimation_user, timedelta_duration):
        if enquiry_user:
            enquiry_user.last_update = timedelta_duration
            enquiry_user.active_time = sum_times([str(timedelta(hours=0, minutes=0, seconds=1)), str(enquiry_user.active_time)]) 
            enquiry_user.updated_at = time()
            
        if estimation_user:
            estimation_user.last_update = timedelta_duration
            estimation_user.active_time = sum_times([str(timedelta(hours=0, minutes=0, seconds=1)), str(enquiry_user.active_time)]) 
            estimation_user.updated_at = time()

    def save_users(self, enquiry_user, estimation_user):
        if estimation_user:
            estimation_user.save()
        if enquiry_user:
            enquiry_user.save()

            
    async def send_data(self, event):
        data = event['data']
        await self.send(data)
    
# @shared_task
class NotificationsConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notification_group = f'notification_user_{self.user_id}'
        await self.channel_layer.group_add(
            self.notification_group,
            self.channel_name
        )
        await self.accept()
        
    # async def disconnect(self, close_code):
    #     await self.channel_layer.group_discard(
    #         self.notification_group,
    #         self.channel_name
    #     )
        # raise StopConsumer()
    async def disconnect(self, close_code):
        try:
            # Handle any necessary cleanup here.
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name
            )
        except Exception as e:
            # Log the exception, so you can investigate any issues during shutdown.
            print(f"Error during WebSocket disconnect: {str(e)}")
        
        # Raise StopConsumer to gracefully stop the consumer.
        raise StopConsumer()
        
    async def receive(self, text_data):
        try:
            data_json = json.loads(text_data)
            notification_data = await self.get_notifications(data_json)
            await self.channel_layer.group_send(
                self.notification_group,
                {
                    'type': 'send_data',
                    'data': json.dumps(notification_data),
                }
            )
        except json.JSONDecodeError:
            print("Invalid JSON format:", text_data)
    
    @database_sync_to_async
    def get_notifications(self, data_json):
        user_obj = User.objects.get(pk=self.user_id)
        user_type = data_json.get('user_type')
        if user_type == 1:
            user = True
            management = False
            notes = EstimationNotes.objects.filter(
                                                    (Q(management=management) & Q(user=user))
                                                ).order_by('-estimation', '-id')
        else:
            management = True
            user = False
            notes = EstimationNotes.objects.filter(
                                                    (Q(estimation__enquiry__enquiry_members=user_obj) | Q(estimation__enquiry__created_by=user_obj)) & 
                                                    (Q(management=management) & Q(user=user))
                                                ).order_by('-estimation', '-id')
            
        notes = notes.filter(note_readed=False).exclude(created_by=user_obj).distinct('estimation')
        data = []
        
        for note in notes:
            note_data = {
                'user': note.created_by.id,
                'message': note.notes,
                'estimation': note.estimation.id,
                'enquiry_id': note.estimation.enquiry.id,
                'enquiry_name': f'{str(note.estimation.enquiry.enquiry_id)} | {str(note.estimation.enquiry.title)}',
                'note_status': note.note_status,
                'note_id': note.id,
                'date_time': note.created_date.strftime('%Y-%m-%d %I:%M %p'),
                'enq_url': reverse('estimation_notes', args=[note.estimation.id]),
                'count': notes.count(),
            }
            data.append(note_data)
        return data
    
    async def send_data(self, event):
        data = event['data']
        await self.send(data)
    

# @shared_task
class EstimationNotesIndication(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.requests_queue = asyncio.Queue()
        self.requests_thread = None
        self.stop_event = asyncio.Event()
        
    async def connect(self):
        self.enquiry_id = self.scope['url_route']['kwargs']['enquiry_id']
        self.temp = self.scope['url_route']['kwargs']['temp']
        
        self.enquiry_notify_group = f'enquiry_notify_{self.enquiry_id}'
        await self.channel_layer.group_add(
            self.enquiry_notify_group,
            self.channel_name
        )
        await self.accept()
        
    # async def disconnect(self, close_code):
    #     await self.channel_layer.group_discard(
    #         self.enquiry_notify_group,
    #         self.channel_name
    #     )
        # raise StopConsumer()
    async def disconnect(self, close_code):
        try:
            # Handle any necessary cleanup here.
            await self.channel_layer.group_discard(
                self.enquiry_notify_group,
                self.channel_name
            )
        except Exception as e:
            # Log the exception, so you can investigate any issues during shutdown.
            print(f"Error during WebSocket disconnect 222: {str(e)}")
        
        # Raise StopConsumer to gracefully stop the consumer.
        # raise StopConsumer()
        
    async def receive(self, text_data):
        try:
            data_json = json.loads(text_data)
            indication = await self.get_notifications(data_json)
            await self.channel_layer.group_send(
                self.enquiry_notify_group,
                {
                    'type': 'send_data',
                    'data': json.dumps(indication),
                }
            )
        except json.JSONDecodeError:
            print("Invalid JSON format:", text_data)
            
    @database_sync_to_async
    def get_notifications(self, data_json):
        user_id = data_json.get('user')
        estimation_id = data_json.get('estimation')
        user_type = data_json.get('user_type')
        if user_type == 1:
            management = True
            user = False
        else:
            management = False
            user = True
        enquiry_obj = Enquiries.objects.get(pk=self.enquiry_id)
        if self.temp == 1:
            EstimationsModels = Temp_Estimations
            EstimationNotesModels = Temp_EstimationNotes
        else:
            EstimationsModels = Estimations
            EstimationNotesModels = EstimationNotes

        estimation = EstimationsModels.objects.filter(enquiry=enquiry_obj)
        have_notes = EstimationNotesModels.objects.filter(
                                        Q(estimation__in=estimation) | Q(enquiry=enquiry_obj.id),
                                        note_readed=False, 
                                        management=management, 
                                        user=user
                                    ).exclude(created_by=user_id)
        
        if estimation_id:
            current_estimation_note = EstimationNotesModels.objects.filter(
                                            Q(estimation=estimation_id) | Q(enquiry=enquiry_obj.id), 
                                            note_readed=False, 
                                            management=management, 
                                            user=user
                                        ).exclude(created_by=user_id)
        else:
            current_estimation_note = 0
        
        return {
            "indication": bool(have_notes),
            "current_estimation": bool(current_estimation_note),
        }
      
        
        
    async def send_data(self, event):
        data = event['data']
        await self.send(data)
        
    
# @shared_task
class EstimationNotesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.estimation_id = self.scope['url_route']['kwargs']['estimation_id']
        self.estimation_group_name = f'estimation_{self.estimation_id}'
        self.temp = self.scope['url_route']['kwargs']['temp']
        
        self.NOTE_STATUS = {
            1: 'Yet to Start',
            2: 'Active',
            3: 'Submitted',
            4: 'Re-Estimating',
            5: 'On Hold',
            6: 'Managment Approved',
            7: 'Discontinued',
            8: 'Reopened',
            9: 'Estimating',
            10: 'Quote',
            12: 'Quotation Sent',
            13: 'Recalled',
            14: 'Customer Approved',
            15: 'Approved with Signature'
        }

        await self.channel_layer.group_add(
            self.estimation_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.estimation_group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        command = data_json.get('command')
        if command == 'get_notes':
            notes = await self.get_notes_list(data_json)
            await self.channel_layer.group_send(
                self.estimation_group_name,
                {
                    'type': 'display_note',
                    'message': notes,
                }
            )
        elif command == 'new_note':
            new_note = await self.create_new_note(data_json)
            await self.channel_layer.group_send(
                self.estimation_group_name,
                {
                    'type': 'send_note',
                    'message': new_note
                }
            )

    @database_sync_to_async
    def get_notes_list(self, data_json):
        user_type = data_json.get('user_type')
        if user_type == 1:
            management = True
            user = False
        else:
            management = False
            user = True
            
        if self.temp != 0:
            EstimationNotesModel = EstimationNotes
            QuotationsModel = Quotations
            EstimationsModel = Estimations
        else:
            EstimationNotesModel = Temp_EstimationNotes
            QuotationsModel = Temp_Quotations
            EstimationsModel = Temp_Estimations
            
        estimation = EstimationsModel.objects.get(pk=self.estimation_id)
        notes = EstimationNotesModel.objects.filter(Q(estimation_id=self.estimation_id) | Q(enquiry=estimation.enquiry.id), management=management, user=user)
        out_data = []
        try:
            quotation_data = QuotationsModel.objects.get(estimations=self.estimation_id)
        except QuotationsModel.DoesNotExist:
            quotation_data = None
        for note in notes:
            status = note.note_status
            notes_data = {
                'type': 'display_note',
                'created_date': note.created_date.strftime("%B %d, %Y, %I:%M %p"),
                'created_by': note.created_by.name,
                'created_by_id': note.created_by.id,
                'note_status_bool': bool(note.note_status),
                'note_status': self.NOTE_STATUS[int(status)],
                'note_status_label': status,
                'quotation_bool': bool(quotation_data),
                'quotation_id': quotation_data.quotation_id if quotation_data else False,
                'estimation_id': note.estimation.id,
                'user_image_bool': bool(note.created_by.image),
                'avathar': '/static/media/avatars/blank.png',
                'user_image_url': note.created_by.image.url if note.created_by.image else False,
                'main_note_bool': bool(note.main_note),
                'main_note': note.main_note if note.main_note else False,
                'note_id': note.id ,
                'main_note_created_by': note.main_note.created_by.name if note.main_note else False,
                'main_note_created_date': note.main_note.created_date if note.main_note else False,
                'notes': note.notes,
                'quotation_url': reverse('estimation_quotations_list', args=[note.estimation.id]) if quotation_data else False,
            }
            
            out_data.append(notes_data)
        return out_data
    async def display_note(self, notes):
        await self.send(text_data=json.dumps({
            'notes': notes
        }))

    @database_sync_to_async
    def create_new_note(self, data_json):
        message = data_json.get('message')
        user_type = message.get('user_type')
        if user_type == 1:
            management = True
            user = False
        else:
            user = True
            management = False
        if self.temp != 0:
            EstimationNotesModel = EstimationNotes
            QuotationsModel = Quotations
        else:
            EstimationNotesModel = Temp_EstimationNotes
            QuotationsModel = Temp_Quotations
            
        if not (message):
            raise ValueError('message is required')
        # with transaction.atomic():
        save_note = EstimationNotesModel.objects.create(
            created_by_id=message.get('created_by', ''),
            estimation_id=self.estimation_id,
            notes=message.get('notes', ''),
            note_status=message.get('note_status', ''),
            management=management, 
            user=user
        )
        save_note.save()
            
        try:
            quotation_data = QuotationsModel.objects.get(estimations=save_note.estimation_id)
        except QuotationsModel.DoesNotExist:
            quotation_data = None

        status = save_note.note_status
        return {
                'type': 'send_note',
                'created_date': save_note.created_date.strftime("%B %d, %Y, %I:%M %p"),
                'created_by': save_note.created_by.name,
                'created_by_id': save_note.created_by.id,
                'note_status_bool': bool(save_note.note_status),
                'note_status_label': self.NOTE_STATUS[int(status)],
                'note_status': status,
                'quotation_bool': bool(quotation_data),
                'quotation_id': quotation_data.quotation_id
                if quotation_data
                else False,
                'estimation_id': save_note.estimation.id,
                'user_image_bool': bool(save_note.created_by.image),
                'avathar': '/static/media/avatars/blank.png',
                'user_image_url': save_note.created_by.image.url
                if save_note.created_by.image
                else False,
                'main_note_bool': bool(save_note.main_note),
                'main_note': save_note.main_note or False,
                'note_id': save_note.id,
                'main_note_created_by': save_note.main_note.created_by.name if save_note.main_note else False,
                'main_note_created_date': save_note.main_note.created_date if save_note.main_note else False,
                'notes': save_note.notes,
                'quotation_url': reverse(
                    'estimation_quotations_list', args=[save_note.estimation.id]
                )
                if quotation_data
                else False,
        }

    async def send_note(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


# @shared_task
class EnquiryNotesConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.enquiry_id = self.scope['url_route']['kwargs']['enquiry_id']
        self.enquiry_group_name = f'enquiry_{self.enquiry_id}'
        
        self.NOTE_STATUS = {
            1: 'Yet to Start',
            2: 'Active',
            3: 'Submitted',
            4: 'Re-Estimating',
            5: 'On Hold',
            6: 'Managment Approved',
            7: 'Discontinued',
            8: 'Reopened',
            9: 'Estimating',
            10: 'Quote',
            12: 'Quotation Sent',
            13: 'Recalled',
            14: 'Customer Approved',
            15: 'Approved with Signature'
        }

        await self.channel_layer.group_add(
            self.enquiry_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.enquiry_group_name,
            self.channel_name
        )
        raise StopConsumer()

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        command = data_json.get('command')
        if command == 'get_notes':
            notes = await self.get_notes_list(data_json)
            await self.channel_layer.group_send(
                self.enquiry_group_name,
                {
                    'type': 'display_note',
                    'message': notes,
                }
            )
        elif command == 'new_note':
            new_note = await self.create_new_note(data_json)
            await self.channel_layer.group_send(
                self.enquiry_group_name,
                {
                    'type': 'send_note',
                    'message': new_note
                }
            )

    @database_sync_to_async
    def get_notes_list(self, data_json):
        version = data_json.get('version', '')
        user_type = data_json.get('user_type')
        if user_type == 1:
            management = True
            user = False
        else:
            management = False
            user = True
            
        enquiry_obj = Enquiries.objects.get(pk=self.enquiry_id)
        estimation = Estimations.objects.filter(enquiry=enquiry_obj)
        
        notes = EstimationNotes.objects.filter(Q(estimation__in=estimation) | Q(enquiry=enquiry_obj.id), management=management, user=user).order_by('id')
        out_data = []
        for note in notes:
            try:
                quotation_data = Quotations.objects.get(estimations=note.estimation.id)
            except Quotations.DoesNotExist:
                quotation_data = None
            status = note.note_status
            notes_data = {
                'type': 'display_note',
                'created_date': note.created_date.strftime("%B %d, %Y, %I:%M %p"),
                'created_by': note.created_by.name,
                'created_by_id': note.created_by.id,
                'note_status_bool': bool(note.note_status),
                'note_status_label': self.NOTE_STATUS[int(status)] if note.note_status else None,
                'note_status': status,
                'quotation_bool': bool(quotation_data),
                'quotation_id': quotation_data.quotation_id if quotation_data else False,
                'estimation_id': note.estimation.id,
                'user_image_bool': bool(note.created_by.image),
                'avathar': '/static/media/avatars/blank.png',
                'user_image_url': note.created_by.image.url if note.created_by.image else False,
                'main_note_bool': bool(note.main_note),
                'main_note': note.main_note.notes if note.main_note else False,
                'note_id': note.id,
                'main_note_created_by': note.main_note.created_by.name if note.main_note else False,
                'main_note_created_date': str(note.main_note.created_date) if note.main_note else False,
                'notes': note.notes,
                'quotation_url': reverse(
                    'estimation_quotations_list', args=[note.estimation.id] if quotation_data else False
                )
            }
            
            out_data.append(notes_data)
        return out_data
    async def display_note(self, notes):
        await self.send(text_data=json.dumps({
            'notes': notes
        }))

    @database_sync_to_async
    def create_new_note(self, data_json):
        if not (message := data_json.get('message')):
            raise ValueError('message is required')

        enquiry_id = Enquiries.objects.get(pk=self.enquiry_id)
        # version = message.get('version', '')
        user_type = message.get('user_type')
        if user_type == 1:
            management = True
            user = False
        else:
            management = False
            user = True
            
        if version := message.get('version', ''):
            estimation = Estimations.objects.get(pk=version)
            main_note = message.get('main_note', '')
            if main_note:
                save_note = EstimationNotes.objects.create(
                    created_by_id=message.get('created_by', ''),
                    estimation_id=message.get('version', ''),
                    notes=message.get('notes', ''),
                    enquiry=enquiry_id,
                    note_status=estimation.version.status,
                    is_replay=True,
                    main_note_id=main_note,
                    management=management,
                    user=user,
                )
            else:
                save_note = EstimationNotes.objects.create(
                    created_by_id=message.get('created_by', ''),
                    estimation_id=message.get('version', ''),
                    notes=message.get('notes', ''),
                    enquiry=enquiry_id,
                    note_status=estimation.version.status,
                    management=management,
                    user=user,
                )
        else:
            save_note = EstimationNotes.objects.create(
                created_by_id=message.get('created_by', ''),
                # estimation_id=message.get('version', ''),
                notes=message.get('notes', ''),
                enquiry=enquiry_id,
                # note_status=estimation.version.status,
                management=management,
                user=user,
            )

        save_note.save()

        try:
            if version := message.get('version', ''):
                quotation_data = Quotations.objects.get(estimations=save_note.estimation.id)
            else:
                quotation_data = None
                
        except Quotations.DoesNotExist:
            quotation_data = None

        status = save_note.note_status
        return {
                    'type': 'send_note',
                    'created_date': save_note.created_date.strftime("%B %d, %Y, %I:%M %p"),
                    'created_by': save_note.created_by.name,
                    'created_by_id': save_note.created_by.id,
                    'note_status_bool': bool(save_note.note_status),
                    'note_status_label': self.NOTE_STATUS[int(status)] if save_note.note_status else None,
                    'note_status': status,
                    'quotation_bool': bool(quotation_data),
                    'quotation_id': quotation_data.quotation_id if quotation_data else False,
                    'estimation_id': save_note.estimation.id if save_note.estimation else None,
                    'user_image_bool': bool(save_note.created_by.image),
                    'avathar': '/static/media/avatars/blank.png',
                    'user_image_url': save_note.created_by.image.url if save_note.created_by.image else False,
                    'main_note_bool': bool(save_note.main_note),
                    'main_note': save_note.main_note.notes if save_note.main_note else False,
                    'note_id': save_note.id,
                    'main_note_created_by': save_note.main_note.created_by.name if save_note.main_note else False,
                    'main_note_created_date': str(save_note.main_note.created_date) if save_note.main_note else False,
                    'notes': save_note.notes,
                    'quotation_url': reverse('estimation_quotations_list', args=[save_note.estimation.id]) if quotation_data else False
            }

    async def send_note(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))