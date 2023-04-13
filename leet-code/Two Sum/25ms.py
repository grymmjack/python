class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        indices = {}
        for i in range(len(nums)):
            curr = nums[i]
            inverseIndex = indices.get(target - curr, -1)
            if inverseIndex >= 0:
                return [inverseIndex, i]
            indices[curr] = i


sol = Solution()
answer = Solution().twoSum([3, 2, 4], 6)

print(answer)
