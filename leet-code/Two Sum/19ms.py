class Solution(object):
    def twoSum(nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        hashmap = {}
        for i in range(len(nums)):
            answer = target - nums[i]
            if answer in hashmap:
                return [i, hashmap[answer]]
            hashmap[nums[i]] = i


answer = Solution.twoSum(nums=[3, 2, 4], target=6)

print(answer)
