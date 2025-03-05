from django.http import JsonResponse
import json
from .models import User, Professor, Module, ModuleInstance, StudentProfessorRating
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Avg

@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data['email']
            username = data['username']
            password = data['password']

            if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'User with this email or username already exists'}, status=400)
            
            user = User.objects.create_user(email=email, username=username, password=password, is_staff=False)
            
            return JsonResponse({'message': 'User registered successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']

            # Authenticate the user
            # Chck if the user exists
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_staff:
                    auth_login(request, user)
                    return JsonResponse({'message': 'Login successful!'}, status=200)
                else:
                    return JsonResponse({'error': 'Admin login not allowed.'}, status=403)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def logout(request):
    try:
        if request.user.is_authenticated:
            auth_logout(request)
            return JsonResponse({'message': 'Logout successful'}, status=200)
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt
def list(request):
    if request.method == 'GET':
        try:
            module_instances = ModuleInstance.objects.all()
            
            custom_module_instance_list = []
            for module_instance in module_instances:
                
                professor_list = module_instance.professors.all()
                custom_prof_list = []
                for professor in professor_list:
                    custom_prof_list.append({
                        'prof_code': professor.prof_code,
                        'prof_first_name': professor.first_name,
                        'prof_last_name': professor.last_name,
                    })

                custom_module_instance_list.append({
                    'module_code': module_instance.module.module_code,
                    'module_name': module_instance.module.module_name,
                    'academic_year': module_instance.academic_year,
                    'semester': module_instance.semester,
                    'prof_list': custom_prof_list,
                })          
            return JsonResponse(custom_module_instance_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def view(request):
    if request.method == 'GET':
        try:
            student_prof_ratings = StudentProfessorRating.objects.all()
            custom_list = []
            prof_list = [] # list of professors who are completed so they don't repeat
            for student_prof_rating in student_prof_ratings:
                if student_prof_rating.professor_id.first_name not in prof_list:
                    rating_name = StudentProfessorRating.objects.filter(professor_id__first_name=student_prof_rating.professor_id.first_name).aggregate(avg_rating=Avg('rating'))
                    custom_list.append({
                        'prof_first_name': student_prof_rating.professor_id.first_name,
                        'prof_last_name': student_prof_rating.professor_id.last_name,
                        'prof_code': student_prof_rating.professor_id.prof_code,
                        'rating': int(rating_name['avg_rating']),
                    })
                prof_list.append(student_prof_rating.professor_id.first_name)

            return JsonResponse(custom_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def average(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            professor_id = data['professor_id']
            module_code = data['module_code']

            # Validation Check
            # Existing module instance
            existing_module_instance = ModuleInstance.objects.filter(
                module__module_code=module_code,
                professors__prof_code=professor_id
            ).exists()       

            if existing_module_instance:
                pass
            else:
                return JsonResponse({'error': 'This professor module combination does not exist'}, status=400)

            filter_prof_ratings = StudentProfessorRating.objects.filter(professor_id__prof_code=professor_id)
            module_prof_ratings = filter_prof_ratings.filter(module_instance_id__module__module_code=module_code)

            average_rating = module_prof_ratings.aggregate(avg_rating=Avg('rating'))

            custom_list = []                    
            custom_list.append({
                'prof_first_name': module_prof_ratings[0].professor_id.first_name,
                'prof_last_name': module_prof_ratings[0].professor_id.last_name,
                'prof_code': professor_id,
                'module_name': module_prof_ratings[0].module_instance_id.module.module_name,
                'module_code': module_code,
                'rating': int(average_rating['avg_rating']),
            })
            return JsonResponse(custom_list, safe=False, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def rate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            professor_code = data['professor_code']
            module_code = data['module_code']
            year = data['year']
            semester = data['semester']
            rating = data['rating']

            # Finding respective values
            student_value = request.user
            prof_value = Professor.objects.get(prof_code=professor_code)
            module_value = Module.objects.get(module_code=module_code)
            filter_module_ratings = ModuleInstance.objects.filter(module=module_value)
            filter_year_ratings = filter_module_ratings.filter(academic_year=year)
            module_instance_value = filter_year_ratings.get(semester=semester) # Final value for module Instance

            # Validation Checks
            existing_module_instance = ModuleInstance.objects.filter(
                professors=prof_value,
                academic_year=module_instance_value.academic_year,
                semester=module_instance_value.semester
            ).exists()
            existing_rating_entry = StudentProfessorRating.objects.filter(
                student_id=student_value,
                professor_id=prof_value,
                module_instance_id=module_instance_value,
            ).exists()

            if existing_module_instance: 
                pass
            else:
                return JsonResponse({'error': 'This professor module combination does not exist.'}, status=400)         

            if existing_rating_entry:
                return JsonResponse({'error': 'You have already rated this professor for this module.'}, status=400)
            
            rating_entry = StudentProfessorRating.objects.create(student_id = student_value, professor_id=prof_value, module_instance_id=module_instance_value, rating=rating)

            return JsonResponse({'message': 'User registered successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)