#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
#      Instagram
#
#    This version: 0.1.0a
#
#       Author: DormantMan
#

import time

from InstagramAPI import InstagramAPI

from config import Config


class Instagram:
    version = '0.1.0a'

    def __init__(self, time_flip_posts=0.75, time_wait_unlock=1800):
        print('Instagram %s' % self.version)
        self.api = InstagramAPI('', '')

        self.time_flip_posts = time_flip_posts
        self.time_wait_unlock = time_wait_unlock

    def get_status(self):
        return self.api.isLoggedIn

    def auth(self, username, password):
        self.api = InstagramAPI(username, password)
        self.api.login(force=True)
        return self.api.isLoggedIn

    def find_user(self, username):
        if self.api.fbUserSearch(username):
            if self.api.LastJson['users']:
                return self.api.LastJson['users'][0]['user']['pk'], username

    def like_feed_user(self, username=None, max_likes=-1, user_id=None):
        if not user_id:
            if username:
                user_id, username = self.find_user(username)
            else:
                return print('User with such a nickname does not exist.')

        self.api.follow(user_id)
        status = self.api.LastJson['friendship_status']
        data = self.find_info_about_user(user_id=user_id)['user']

        print('####################################################\n')
        print('User: {username} [{user_id}]{blocking}{followed_by}{following}{is_private}'.format(
            username=username,
            user_id=user_id,
            blocking=('\nThis user has blocked you' if status['blocking'] else ''),
            followed_by=('\nFollowed: OK' if status['followed_by'] else '\nFollowed: ×'),
            following=('\nFollowing: OK' if status['following'] else '\nFollowing: ×'),
            is_private=('\nPrivate account: YES' if status['is_private'] else '\nPrivate account: NO')
        ))
        print('\n\tINFO:{full_name}{posts}{followers}{following}{image}'.format(
            full_name='\nFull Name: %s' % data['full_name'],
            posts='\nPosts: %s' % data['media_count'],
            followers='\nFollowers: %s' % data['follower_count'],
            following='\nFollowings: %s' % data['following_count'],
            image='\nImage: %s' % (data['hd_profile_pic_url_info']['url'] if 'hd_profile_pic_url_info'
                                                                             '' in data else None),

        ))
        print('\n####################################################')

        if self.api.getUserFeed(user_id):
            media_count = data['media_count']
            sum_likes = 0
            now_count = 0
            max_id = ''
            total = 0

            print(f'Starting liking {username}\'s media...')

            while True:
                if max_id == 'end':
                    return print(f'Mission complete :)\n'
                                 f'[Posts ended]\n'
                                 f'Result: {total}/{media_count} ({round(total/media_count*100, 2)}%)\n'
                                 f'The average of likes: {round(sum_likes/media_count, 2)}')

                self.api.getUserFeed(user_id, maxid=max_id)
                media = self.api.LastJson

                max_id = 'end' if 'next_max_id' not in media else media['next_max_id']

                media = media['items']

                # media_count += len(media)

                self.log(f'Total media count: {media_count}')

                for post in media:
                    if now_count >= max_likes >= 0:
                        return print(f'Mission complete :)\n'
                                     f'[The maximum is reached]\n'
                                     f'Result: {total}/{now_count} ({round(total/now_count*100, 2)}%)\n'
                                     f'The average of likes: {round(sum_likes/now_count, 2)}')
                    now_count += 1

                    media_id = post['pk']
                    likes = post['like_count']
                    pinpoint = time.process_time()

                    sum_likes += likes

                    if post['has_liked']:
                        self.log(f'\r{now_count}\t-\tMedia {media_id} [likes:{likes}]\t[old like] *')

                    else:
                        while True:
                            try:
                                if self.api.like(media_id):
                                    total += 1
                                    self.log(f'\r{now_count}\t-\tMedia {media_id} [likes:{likes}]\t[new like] +')
                                    time.sleep(min(pinpoint - self.time_flip_posts, 0))
                                break

                            except (Exception, BaseException):
                                print('\nAccount temporarily blocked')
                                print('Time to wait for unlock: {}'.format(self.time_wait_unlock))

                                pinpoint = time.process_time()
                                while (time.process_time() - pinpoint) < self.time_wait_unlock:
                                    self.log('\rTime left: {} s'.format(round(time.process_time() - pinpoint)))

                                print('Try again...')

                self.log(f'Liked {total}/{media_count} media')
        else:
            print('Unable to get user\'s feed.')

    def find_info_about_user(self, username=None, user_id=None):
        if not user_id:
            if username:
                user_id, username = self.find_user(username)
            else:
                return print('User with such a nickname does not exist.')

        self.api.getUsernameInfo(user_id)
        return self.api.LastJson

    @staticmethod
    def log(s):
        print(s)
        # sys.stdout.flush()

    def logout(self):
        self.api.logout()


if __name__ == '__main__':
    client = Instagram(time_flip_posts=1.25, time_wait_unlock=1800)
    client.auth(Config.username, Config.password)

    s_username = input('Input username: ')
    client.like_feed_user(username=s_username, max_likes=-1)
