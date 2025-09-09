import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from marketing_bot.models.campaign import Campaign, CampaignType, CampaignStatus
from marketing_bot.services.campaign_service import CampaignService
from marketing_bot.repositories.campaign_repository import CampaignRepository
from marketing_bot.metrics.tracker import MetricsTracker


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=CampaignRepository)


@pytest.fixture
def mock_metrics():
    return AsyncMock(spec=MetricsTracker)


@pytest.fixture
def campaign_service(mock_repo, mock_metrics):
    return CampaignService(mock_repo, mock_metrics)


@pytest.fixture
def sample_campaign():
    return Campaign(
        name="Test Campaign",
        campaign_type=CampaignType.EMAIL,
        segment_name="champions",
        product_name="Test Product",
        goal="Test Goal",
        offer="Test Offer"
    )


@pytest.mark.asyncio
async def test_create_campaign(campaign_service, mock_repo, sample_campaign):
    mock_repo.create.return_value = sample_campaign
    
    result = await campaign_service.create_campaign(sample_campaign)
    
    assert result == sample_campaign
    mock_repo.create.assert_called_once_with(sample_campaign)


@pytest.mark.asyncio
async def test_get_campaign(campaign_service, mock_repo, sample_campaign):
    campaign_id = uuid4()
    mock_repo.get_by_id.return_value = sample_campaign
    
    result = await campaign_service.get_campaign(campaign_id)
    
    assert result == sample_campaign
    mock_repo.get_by_id.assert_called_once_with(campaign_id)


@pytest.mark.asyncio
async def test_list_campaigns(campaign_service, mock_repo, sample_campaign):
    mock_repo.list.return_value = [sample_campaign]
    
    result = await campaign_service.list_campaigns()
    
    assert len(result) == 1
    assert result[0] == sample_campaign
    mock_repo.list.assert_called_once_with(status=None)


def test_split_email():
    service = CampaignService(None, None)
    
    content = "Subject: Test Subject\n\nThis is the body content."
    subject, body = service._split_email(content)
    
    assert subject == "Test Subject"
    assert body == "This is the body content."
