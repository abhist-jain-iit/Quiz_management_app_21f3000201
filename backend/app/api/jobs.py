from flask import request, jsonify, current_app, send_file
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..decorators import admin_required
from ..tasks import export_user_csv, export_admin_csv
from celery.result import AsyncResult
import os

class UserCSVExportApi(Resource):
    @jwt_required()
    def post(self):
        """Trigger user CSV export job"""
        current_user_id = get_jwt_identity()
        
        try:
            # Start the background job
            task = export_user_csv.delay(current_user_id)
            
            return {
                'message': 'CSV export started',
                'task_id': task.id,
                'status': 'PENDING'
            }, 202
            
        except Exception as e:
            return {'message': f'Failed to start export: {str(e)}'}, 500

class AdminCSVExportApi(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Trigger admin CSV export job"""
        current_user_id = get_jwt_identity()

        try:
            # Start the background job with admin user ID
            task = export_admin_csv.delay(current_user_id)

            return {
                'message': 'Admin CSV export started',
                'task_id': task.id,
                'status': 'PENDING'
            }, 202

        except Exception as e:
            return {'message': f'Failed to start export: {str(e)}'}, 500

class JobStatusApi(Resource):
    @jwt_required()
    def get(self, task_id):
        """Get job status and result"""
        try:
            task = AsyncResult(task_id, app=current_app.celery)
            
            if task.state == 'PENDING':
                response = {
                    'state': task.state,
                    'status': 'Job is waiting to be processed'
                }
            elif task.state == 'PROGRESS':
                response = {
                    'state': task.state,
                    'progress': task.info.get('progress', 0),
                    'status': task.info.get('status', 'Processing...')
                }
            elif task.state == 'SUCCESS':
                response = {
                    'state': task.state,
                    'result': task.result,
                    'status': 'Job completed successfully'
                }
            else:  # FAILURE
                response = {
                    'state': task.state,
                    'error': str(task.info),
                    'status': 'Job failed'
                }
            
            return response, 200
            
        except Exception as e:
            return {'message': f'Failed to get job status: {str(e)}'}, 500

class DownloadCSVApi(Resource):
    @jwt_required()
    def get(self, filename):
        """Download CSV file"""
        try:
            file_path = os.path.join('exports', filename)
            
            if not os.path.exists(file_path):
                return {'message': 'File not found'}, 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='text/csv'
            )
            
        except Exception as e:
            return {'message': f'Failed to download file: {str(e)}'}, 500

class TriggerDailyRemindersApi(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Manually trigger daily reminders (for testing)"""
        try:
            from ..tasks import send_daily_reminders
            task = send_daily_reminders.delay()
            
            return {
                'message': 'Daily reminders job started',
                'task_id': task.id,
                'status': 'PENDING'
            }, 202
            
        except Exception as e:
            return {'message': f'Failed to start reminders: {str(e)}'}, 500

class TriggerMonthlyReportsApi(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Manually trigger monthly reports (for testing)"""
        try:
            from ..tasks import generate_monthly_reports
            task = generate_monthly_reports.delay()
            
            return {
                'message': 'Monthly reports job started',
                'task_id': task.id,
                'status': 'PENDING'
            }, 202
            
        except Exception as e:
            return {'message': f'Failed to start reports: {str(e)}'}, 500
