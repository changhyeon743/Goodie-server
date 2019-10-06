from django.contrib import admin

# Register your models here.
## models에서 BlogData를 import 해옵니다.
from .models import Video

## 아래의 코드를 입력하면 BlogData를 admin 페이지에서 관리할 수 있습니다.
admin.site.register(Video)