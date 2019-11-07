# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List

from botbuilder.schema import ActivityTypes, ChannelAccount, MessageReaction
from botbuilder.core.turn_context import TurnContext
from botbuilder.core import ActivityHandler, MessageFactory
from botbuilder.schema.teams import TeamInfo, ChannelInfo, TeamsChannelData, TenantInfo, TeamsChannelAccount
from botframework.connector import Channels
from http import HTTPStatus
from botbuilder.core import InvokeResponse

from pprint import pprint
import jsonpickle

class TeamsActivityHandler(ActivityHandler):
    async def on_turn(self, turn_context: TurnContext):
        if turn_context is None:
            raise TypeError("ActivityHandler.on_turn(): turn_context cannot be None.")

   
        if hasattr(turn_context, "activity") and turn_context.activity is None:
            raise TypeError(
                "ActivityHandler.on_turn(): turn_context must have a non-None activity."
            )

        if (
            hasattr(turn_context.activity, "type")
            and turn_context.activity.type is None
        ):
            raise TypeError(
                "ActivityHandler.on_turn(): turn_context activity must have a non-None type."
            )

        if turn_context.activity.type == ActivityTypes.invoke:
            invokeResponse = await on_invoke_activity(turn_context)
        else:
            await super().on_turn(turn_context)
        

    async def on_invoke_activity(turn_context: TurnContext):
        try:
            if turn_context.activity.name == None and turn_context.activity.channel_id == Channels.Msteams:
                return #await on_teams_card_action_invoke_activity(turn_context)
            else:
                turn_context.send_activity(MessageFactory.text("working"))
        except:
            return
    
    async def on_conversation_update_activity(self, turn_context: TurnContext):
        print(turn_context.activity)
        if turn_context.activity.channel_id == Channels.ms_teams:
            channel_data = TeamsChannelData(**turn_context.activity.channel_data)

            if turn_context.activity.members_added != None:
                return await self.on_teams_members_added_dispatch_activity(turn_context.activity.members_added, channel_data.team, turn_context)

            if turn_context.activity.members_removed != None:
                return await self.on_teams_members_removed_dispatch_activity(turn_context.activity.members_removed, channel_data.team, turn_context)
            
            if channel_data != None:
                if channel_data.event_type == "channelCreated":
                    return await self.on_teams_channel_created_activity(channel_data.channel, channel_data.team, turn_context)
                elif channel_data.event_type == "channelDeleted":
                    return await self.on_teams_channel_deleted_activity(channel_data.channel, channel_data.team, turn_context)
                elif channel_data.event_type == "channelRenamed":
                    return await self.on_teams_channel_renamed_activity(channel_data.channel, channel_data.team, turn_context)
                elif channel_data.event_type == "teamRenamed":
                    return await self.on_teams_team_renamed_activity(channel_data.team, turn_context)
                else:
                    return await super().on_conversation_update_activity(turn_context)
        
        return await super().on_conversation_update_activity(turn_context)
    
    async def on_teams_channel_created_activity(self, channel_info: ChannelInfo, team_info: TeamInfo, turn_context: TurnContext):
        return
    
    async def on_teams_team_renamed_activity(self, team_info: TeamInfo, turn_context: TurnContext):
        return

    async def on_teams_members_added_dispatch_activity(self, members_added: [ChannelAccount], team_info: TeamInfo, turn_context: TurnContext):
        """
        team_members = {}
        team_members_added = []
        for member in members_added:
            if member.additional_properties != {}:
                team_members_added.append(TeamsChannelAccount(member))
            else:
                if team_members == {}:
                    result = await TeamsInfo.get_members_async(turn_context)
                    team_members = { i.id : i for i in result }
                
                if member.id in team_members:
                    team_members_added.append(member)
                else:
                    newTeamsChannelAccount = TeamsChannelAccount(
                        id=member.id, 
                        name = member.name, 
                        aad_object_id = member.aad_object_id,
                        role = member.role
                        )
                    team_members_added.append(newTeamsChannelAccount)
        
        return await self.on_teams_members_added_activity(teams_members_added, team_info, turn_context)
        """
        for member in members_added:
            newAccountJson = member.__dict__
            del newAccountJson["additional_properties"] 
            member = TeamsChannelAccount(**newAccountJson)
        return await self.on_teams_members_added_activity(members_added, turn_context)

    async def on_teams_members_added_activity(self, teams_members_added: [TeamsChannelAccount], turn_context: TurnContext):
        for member in teams_members_added:
            member = ChannelAccount(member)
        return super().on_members_added_activity(members_added, turn_context)

    async def on_teams_members_removed_dispatch_activity(self, members_removed: List, team_info: TeamInfo, turn_context: TurnContext):
        teams_members_removed = []
        for member in members_removed:
            newAccountJson = member.__dict__
            del newAccountJson["additional_properties"]
            teams_members_removed.append(TeamsChannelAccount(**newAccountJson))

        return await self.on_teams_members_removed_activity(teams_members_removed, turn_context)

    async def on_teams_members_removed_activity(self, teams_members_removed: [TeamsChannelAccount], turn_context: TurnContext):
        members_removed = [ ChannelAccount(i) for i in teams_members_removed ]
        return super().on_members_removed_activity(members_removed, turn_context)

    
    

    async def on_teams_channel_deleted_activity(self, channel_info: ChannelInfo, team_info: TeamInfo, turn_context: TurnContext):
        return #Task.CompleteTask

    async def on_teams_channel_renamed_activity(self, channel_info: ChannelInfo, team_info: TeamInfo, turn_context: TurnContext):
        return #Task.CompleteTask

    async def on_teams_team_reanamed_async(self, teamInfo: TeamInfo, turn_context: TurnContext):
        return #Task.CompleteTask

    @staticmethod
    def _create_invoke_response(body: object = None) -> InvokeResponse:
        return InvokeResponse(status = int(HTTPStatus.OK), body = body)
    
    class _InvokeResponseException(Exception):
        def __init__(self, status_code: HTTPStatus, body: object = None):
            self._statusCode = status_code
            self._body = body

        def create_invoke_response() -> InvokeResponse:
            return InvokeResponse(status= int(self._statusCode), body = self._body)