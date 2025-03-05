from rest_framework import serializers
from .models import Poll, Option, Vote
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
    
    def partial_update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().partial_update(instance, validated_data)

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['text', 'id']

        def validate_text(self, text):
            poll = self.context.get('poll')
            if poll and poll.options.filter(text__iexact=text).exists():
                raise serializers.ValidationError("This option already exists")
            return text

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
        extra_kwargs = {
            'poll': {'required': False}
        }

    def validate(self, data):
        poll = self.context.get('poll')
        user = self.context.get('user')
        option = data.get('option')
        ip_hash = data.get('ip_hash')
        session_id = data.get('session_id')

        data['poll'] = poll
        data['voted_by'] = user

        if not poll.expire_date or poll.expire_date < timezone.now():
            raise serializers.ValidationError("This poll has already expired")
        
        if user:
            if poll.votes.filter(voted_by=user).exists():
                raise serializers.ValidationError("You have already voted in this poll")
        elif ip_hash and session_id:
            if poll.votes.filter(ip_hash=ip_hash, session_id=session_id).exists():
                raise serializers.ValidationError("You have already voted in this poll")
        else:
            raise serializers.ValidationError("You must be either authenticated or provide an IP address and session ID")
        
        if option not in poll.options.all():
            raise serializers.ValidationError("This option is not part of the poll")
        return data

class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'created_by', 'pub_date', 'expire_date', 'options']
        read_only_fields = ['created_by', 'pub_date']
    
    def validate_options(self, options):
        if len(options) < 2:
            raise serializers.ValidationError("A poll must have at least two options")
        return options
    
    def create(self, validated_data):
        options = validated_data.pop('options')

        validated_data['created_by'] = self.context['request'].user

        with transaction.atomic():
            poll = Poll.objects.create(**validated_data)
            for option in options:
                Option.objects.create(poll=poll, **option)
        return poll
    
    def update(self, instance, validated_data):
        options = validated_data.pop('options')

        # Remove fields that should not be updated
        validated_data.pop('created_by', None)
        validated_data.pop('pub_date', None)

        with transaction.atomic():
            instance.title = validated_data.get('title', instance.title)
            instance.description = validated_data.get('description', instance.description)
            instance.expire_date = validated_data.get('expire_date', instance.expire_date)
            instance.save()

            existing_options = {opt.id: opt for opt in instance.options.all()}
            for option in options:
                if 'id' in option:
                    opt = existing_options.pop(option['id'])
                    opt.text = option.get('text', opt.text)
                    opt.save()
                else:
                    Option.objects.create(poll=instance, **option)
            for opt in existing_options.values():
                opt.delete()
        return instance