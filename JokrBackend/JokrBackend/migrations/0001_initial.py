# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import JokrBackend.Custom.ModelFields
import JokrBackend.Custom.Utils


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedContent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=None)),
                ('timeArchived', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('timeOriginalCreated', models.IntegerField(default=None)),
                ('key', models.CharField(max_length=36, default=None)),
                ('contentType', models.CharField(max_length=2, default=None)),
                ('fav', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Gravity_content_archived',
            },
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('timeBanExpires', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_moderation_ban',
            },
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
            ],
            options={
                'db_table': 'Gravity_moderation_block',
            },
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('file', models.CharField(max_length=40, default=None)),
                ('lineNum', models.IntegerField(default=None)),
                ('exeptionMessage', models.TextField(default=None)),
                ('stackTrace', models.TextField(default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_error',
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('text', models.CharField(max_length=500, default=None)),
            ],
            options={
                'db_table': 'Gravity_analytics_feedback',
            },
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('url', models.CharField(max_length=30, default=None)),
                ('responseCode', models.SmallIntegerField(null=True, default=None)),
                ('messageCode', models.CharField(max_length=10, null=True, default=None)),
                ('ip', models.GenericIPAddressField(default=None)),
            ],
            options={
                'db_table': 'Gravity_security_hit',
            },
        ),
        migrations.CreateModel(
            name='LocalPostsPrunedEvent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('messageCode', models.CharField(max_length=10, default=None)),
                ('numOldPosts', models.IntegerField(default=None)),
                ('numDeletedPosts', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_event_localpostsPruned',
            },
        ),
        migrations.CreateModel(
            name='MessagesPrunedEvent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('messageCode', models.CharField(max_length=10, default=None)),
                ('numOldMessages', models.IntegerField(default=None)),
                ('numDeletedMessages', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_event_messagesPruned',
            },
        ),
        migrations.CreateModel(
            name='ModAction',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('result', models.CharField(max_length=3, default=None)),
                ('contentID', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, default=None)),
                ('contentType', models.CharField(max_length=2, default=None)),
            ],
            options={
                'db_table': 'Gravity_moderation_modAction',
            },
        ),
        migrations.CreateModel(
            name='NotificationSentEvent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('messageCode', models.CharField(max_length=10, default=None)),
                ('deliveryType', models.CharField(max_length=5, default=None)),
                ('notificationType', models.CharField(max_length=7, default=None)),
                ('numCollapsedNotifcations', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_event_notificationSent',
            },
        ),
        migrations.CreateModel(
            name='OnlineContent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('key', models.CharField(max_length=36, null=True, default=None)),
                ('contentType', models.CharField(max_length=2, default=None)),
                ('fav', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'Gravity_content_online',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('contentID', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, default=None)),
                ('contentType', models.CharField(max_length=2, default=None)),
            ],
            options={
                'db_table': 'Gravity_moderation_report',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('timeExpires', models.IntegerField(default=None)),
                ('token', models.CharField(max_length=870, default=None)),
            ],
            options={
                'db_table': 'Gravity_security_session',
            },
        ),
        migrations.CreateModel(
            name='StaticContentPrunedEvent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('messageCode', models.CharField(max_length=10, default=None)),
                ('numRequestedForDeleteion', models.IntegerField(default=None)),
                ('numDeleted', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_event_staticContentPruned',
            },
        ),
        migrations.CreateModel(
            name='ThreadPrunedEvent',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('threadID', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, default=None)),
            ],
            options={
                'db_table': 'Gravity_logging_event_threadPruned',
            },
        ),
        migrations.CreateModel(
            name='TimeLastNotifcationSent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeLastSent', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'Gravity_notification_timeLastSent',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', JokrBackend.Custom.ModelFields.UUIDField(max_length=16, primary_key=True, serialize=False, default=JokrBackend.Custom.Utils.CreateSequentialUUIDForDB)),
                ('timeCreated', models.IntegerField(default=JokrBackend.Custom.Utils.CreateTimestampForDB)),
                ('timeLastLogin', models.IntegerField(null=True, default=None)),
            ],
            options={
                'db_table': 'Gravity_security_user',
            },
        ),
        migrations.CreateModel(
            name='ArchivedLocalPost',
            fields=[
                ('archivedContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.ArchivedContent')),
                ('latitude', models.DecimalField(decimal_places=6, default=None, max_digits=9, db_index=True)),
                ('longitude', models.DecimalField(decimal_places=6, default=None, max_digits=9, db_index=True)),
                ('text', models.CharField(max_length=500, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_archived_localpost',
            },
            bases=('JokrBackend.archivedcontent',),
        ),
        migrations.CreateModel(
            name='ArchivedMessage',
            fields=[
                ('archivedContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.ArchivedContent')),
                ('text', models.CharField(max_length=500, default=None)),
                ('toUser', models.ForeignKey(to='JokrBackend.User', related_name='+', default=None)),
            ],
            options={
                'db_table': 'Gravity_content_archived_message',
            },
            bases=('JokrBackend.archivedcontent',),
        ),
        migrations.CreateModel(
            name='ArchivedReply',
            fields=[
                ('archivedContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.ArchivedContent')),
                ('text', models.CharField(max_length=500, null=True, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_archived_reply',
            },
            bases=('JokrBackend.archivedcontent',),
        ),
        migrations.CreateModel(
            name='ArchivedThread',
            fields=[
                ('archivedContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.ArchivedContent')),
                ('arn', models.CharField(max_length=256, default=None)),
                ('text', models.CharField(max_length=500, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_archived_thread',
            },
            bases=('JokrBackend.archivedcontent',),
        ),
        migrations.CreateModel(
            name='LocalPost',
            fields=[
                ('onlineContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.OnlineContent')),
                ('latitude', models.DecimalField(decimal_places=6, default=None, max_digits=9, db_index=True)),
                ('longitude', models.DecimalField(decimal_places=6, default=None, max_digits=9, db_index=True)),
                ('text', models.CharField(max_length=500, default=None)),
                ('arn', models.CharField(max_length=256, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_online_localpost',
            },
            bases=('JokrBackend.onlinecontent',),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('onlineContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.OnlineContent')),
                ('text', models.CharField(max_length=500, default=None)),
                ('toUser', models.ForeignKey(to='JokrBackend.User', related_name='+', default=None)),
            ],
            options={
                'db_table': 'Gravity_content_online_message',
            },
            bases=('JokrBackend.onlinecontent',),
        ),
        migrations.CreateModel(
            name='Reply',
            fields=[
                ('onlineContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.OnlineContent')),
                ('text', models.CharField(max_length=500, null=True, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_online_reply',
            },
            bases=('JokrBackend.onlinecontent',),
        ),
        migrations.CreateModel(
            name='SecurityErrorHit',
            fields=[
                ('hit', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.Hit')),
                ('requestMethod', models.CharField(max_length=10, default=None)),
                ('requestContentType', models.CharField(max_length=50, default=None)),
                ('requestData', models.TextField(default=None)),
                ('errors', models.CharField(max_length=30, default=None)),
            ],
            options={
                'db_table': 'Gravity_security_hit_securityError',
            },
            bases=('JokrBackend.hit',),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('onlineContent', models.OneToOneField(parent_link=True, primary_key=True, serialize=False, to='JokrBackend.OnlineContent')),
                ('text', models.CharField(max_length=500, default=None)),
                ('arn', models.CharField(max_length=256, default=None)),
            ],
            options={
                'db_table': 'Gravity_content_online_thread',
            },
            bases=('JokrBackend.onlinecontent',),
        ),
        migrations.AddField(
            model_name='session',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='report',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='report',
            name='modAction',
            field=models.ForeignKey(to='JokrBackend.ModAction', related_name='+', null=True, default=None),
        ),
        migrations.AddField(
            model_name='onlinecontent',
            name='fromSession',
            field=models.ForeignKey(to='JokrBackend.Session', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='onlinecontent',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='hit',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', null=True, default=None),
        ),
        migrations.AddField(
            model_name='hit',
            name='session',
            field=models.ForeignKey(to='JokrBackend.Session', related_name='+', null=True, default=None),
        ),
        migrations.AddField(
            model_name='feedback',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='block',
            name='blockedUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='block',
            name='blockerUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='ban',
            name='bannedUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='archivedcontent',
            name='fromSession',
            field=models.ForeignKey(to='JokrBackend.Session', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='archivedcontent',
            name='fromUser',
            field=models.ForeignKey(to='JokrBackend.User', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='reply',
            name='parentThread',
            field=models.ForeignKey(to='JokrBackend.Thread', related_name='+', default=None),
        ),
        migrations.AddField(
            model_name='archivedreply',
            name='parentThread',
            field=models.ForeignKey(to='JokrBackend.ArchivedThread', related_name='+', default=None),
        ),
    ]
